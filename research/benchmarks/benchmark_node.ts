/**
 * AryaCrypt research benchmark (Node/TypeScript) — measured timings only.
 * Run from repo: npx tsx research/benchmarks/benchmark_node.ts
 */

import { performance } from "node:perf_hooks";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { cpus, platform, release, arch, totalmem } from "node:os";
import { createRequire } from "node:module";

import { AryaCrypt } from "../../node-sdk/src/AryaCrypt.ts";
import * as preprocess from "../../node-sdk/src/preprocess.ts";
import * as kdf from "../../node-sdk/src/kdf.ts";
import * as aesGcm from "../../node-sdk/src/aesGcm.ts";
import * as aryaFormat from "../../node-sdk/src/format.ts";
import {
  ALGORITHM_ID,
  FRAMEWORK_VERSION,
  LEGACY_ALGORITHM_ID,
} from "../../node-sdk/src/constants.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const RESULTS_DIR = join(__dirname, "results");

const PASSWORD = "password1";
const SALT = Buffer.from("00112233445566778899aabbccddeeff", "hex");
const NONCE = Buffer.from("0102030405060708090a0b0c", "hex");
const PLAINTEXT_SEED = 42;

const SIZE_LABELS: Record<number, string> = {
  1024: "1KB",
  [100 * 1024]: "100KB",
  [1024 * 1024]: "1MB",
  [10 * 1024 * 1024]: "10MB",
  [100 * 1024 * 1024]: "100MB",
};

const DEFAULT_SIZES = Object.keys(SIZE_LABELS).map(Number);
const QUICK_SIZES = [1024, 100 * 1024, 1024 * 1024];

function sizeLabel(n: number): string {
  return SIZE_LABELS[n] ?? `${n}B`;
}

function defaultRuns(size: number): number {
  if (size <= 1024 * 1024) return 10;
  if (size <= 10 * 1024 * 1024) return 5;
  return 3;
}

function shouldWarmup(size: number): boolean {
  return size < 100 * 1024 * 1024;
}

function makePlaintext(size: number, seed = PLAINTEXT_SEED): Buffer {
  const out = Buffer.alloc(size);
  let state = seed >>> 0;
  for (let i = 0; i < size; i++) {
    state ^= (state << 13) >>> 0;
    state ^= state >>> 17;
    state ^= (state << 5) >>> 0;
    out[i] = state & 0xff;
  }
  return out;
}

function summarize(samples: number[]) {
  if (!samples.length) {
    return { mean: null, median: null, min: null, max: null, stdev: null, n: 0 };
  }
  const sorted = [...samples].sort((a, b) => a - b);
  const n = sorted.length;
  const mean = samples.reduce((a, b) => a + b, 0) / n;
  const mid = Math.floor(n / 2);
  const median = n % 2 ? sorted[mid]! : (sorted[mid - 1]! + sorted[mid]!) / 2;
  let stdev = 0;
  if (n > 1) {
    const v = samples.reduce((a, b) => a + (b - mean) ** 2, 0) / (n - 1);
    stdev = Math.sqrt(v);
  }
  return {
    mean,
    median,
    min: sorted[0]!,
    max: sorted[n - 1]!,
    stdev,
    n,
  };
}

function throughputMbs(sizeBytes: number, seconds: number | null): number | null {
  if (seconds == null || seconds <= 0) return null;
  return sizeBytes / 1_000_000 / seconds;
}

function overheadPct(arya: number | null, baseline: number | null): number | null {
  if (arya == null || baseline == null || baseline <= 0) return null;
  return ((arya - baseline) / baseline) * 100;
}

async function timeAsync<T>(fn: () => Promise<T> | T): Promise<[T, number]> {
  const t0 = performance.now();
  const result = await fn();
  return [result, (performance.now() - t0) / 1000];
}

async function runAryacryptStaged(plaintext: Buffer) {
  const [, tPre] = await timeAsync(() => preprocess.transformPassword(PASSWORD));
  const { stream } = preprocess.transformPassword(PASSWORD);
  const [key, tKdf] = await timeAsync(() => kdf.deriveKey(stream, SALT));
  const [enc, tEnc] = await timeAsync(() =>
    aesGcm.encryptBytes(key, NONCE, plaintext)
  );
  const [pt, tDec] = await timeAsync(() =>
    aesGcm.decryptBytes(key, NONCE, enc.tag, enc.ciphertext)
  );
  if (!pt.equals(plaintext)) throw new Error("decrypt mismatch");
  const stagedSum = tPre + tKdf + tEnc;
  return {
    path: "aryacrypt",
    t_preprocess: tPre,
    t_kdf: tKdf,
    t_aes_enc: tEnc,
    t_aes_dec: tDec,
    t_staged_enc_sum: stagedSum,
    preprocess_share: stagedSum > 0 ? tPre / stagedSum : null,
    throughput_aes_enc_mbs: throughputMbs(plaintext.length, tEnc),
    throughput_aes_dec_mbs: throughputMbs(plaintext.length, tDec),
  };
}

async function runBaselineStaged(plaintext: Buffer) {
  const material = Buffer.from(PASSWORD, "utf8");
  const [key, tKdf] = await timeAsync(() => kdf.deriveKey(material, SALT));
  const [enc, tEnc] = await timeAsync(() =>
    aesGcm.encryptBytes(key, NONCE, plaintext)
  );
  const [pt, tDec] = await timeAsync(() =>
    aesGcm.decryptBytes(key, NONCE, enc.tag, enc.ciphertext)
  );
  if (!pt.equals(plaintext)) throw new Error("decrypt mismatch");
  return {
    path: "baseline",
    t_preprocess: 0,
    t_kdf: tKdf,
    t_aes_enc: tEnc,
    t_aes_dec: tDec,
    t_staged_enc_sum: tKdf + tEnc,
    preprocess_share: 0,
    throughput_aes_enc_mbs: throughputMbs(plaintext.length, tEnc),
    throughput_aes_dec_mbs: throughputMbs(plaintext.length, tDec),
  };
}

async function runE2eAryacrypt(crypto: AryaCrypt, plaintext: Buffer) {
  const [blob, tEnc] = await timeAsync(() =>
    crypto.encrypt(plaintext, PASSWORD, {
      salt: SALT,
      nonce: NONCE,
      timestamp: 1_700_000_000,
    })
  );
  const [pt, tDec] = await timeAsync(() => crypto.decrypt(blob, PASSWORD));
  if (!Buffer.from(pt).equals(plaintext)) throw new Error("e2e decrypt mismatch");
  return {
    t_total_enc: tEnc,
    t_total_dec: tDec,
    throughput_e2e_enc_mbs: throughputMbs(plaintext.length, tEnc),
    throughput_e2e_dec_mbs: throughputMbs(plaintext.length, tDec),
    blob_bytes: blob.length,
  };
}

async function runE2eBaseline(plaintext: Buffer) {
  const [blob, tEnc] = await timeAsync(async () => {
    const key = await kdf.deriveKey(Buffer.from(PASSWORD, "utf8"), SALT);
    const { ciphertext, tag } = aesGcm.encryptBytes(key, NONCE, plaintext);
    const meta = aryaFormat.buildMetadata(SALT, NONCE, tag, {
      algorithm: LEGACY_ALGORITHM_ID,
      timestamp: 1_700_000_000,
    });
    return Buffer.concat([aryaFormat.serializeHeader(meta), ciphertext]);
  });
  const [pt, tDec] = await timeAsync(async () => {
    const { metadata, ciphertext } = aryaFormat.parseContainer(blob);
    const salt = aryaFormat.decodeB64Field(metadata, "salt");
    const nonce = aryaFormat.decodeB64Field(metadata, "nonce");
    const tag = aryaFormat.decodeB64Field(metadata, "auth_tag");
    const key = await kdf.deriveKey(Buffer.from(PASSWORD, "utf8"), salt);
    return aesGcm.decryptBytes(key, nonce, tag, ciphertext);
  });
  if (!pt.equals(plaintext)) throw new Error("baseline e2e mismatch");
  return {
    t_total_enc: tEnc,
    t_total_dec: tDec,
    throughput_e2e_enc_mbs: throughputMbs(plaintext.length, tEnc),
    throughput_e2e_dec_mbs: throughputMbs(plaintext.length, tDec),
    blob_bytes: blob.length,
  };
}

function aggregate(runs: Record<string, number | null>[], keys: string[]) {
  const out: Record<string, ReturnType<typeof summarize>> = {};
  for (const key of keys) {
    const vals = runs
      .map((r) => r[key])
      .filter((v): v is number => typeof v === "number");
    out[key] = summarize(vals);
  }
  return out;
}

const METRIC_KEYS = [
  "t_preprocess",
  "t_kdf",
  "t_aes_enc",
  "t_aes_dec",
  "t_staged_enc_sum",
  "t_total_enc",
  "t_total_dec",
  "throughput_aes_enc_mbs",
  "throughput_aes_dec_mbs",
  "throughput_e2e_enc_mbs",
  "throughput_e2e_dec_mbs",
  "preprocess_share",
];

async function benchmarkSize(size: number, runs: number, crypto: AryaCrypt) {
  const plaintext = makePlaintext(size);
  const label = sizeLabel(size);
  console.log(`  [${label}] size=${size} runs=${runs} ...`);

  if (shouldWarmup(size)) {
    await runAryacryptStaged(plaintext);
    await runBaselineStaged(plaintext);
    await runE2eAryacrypt(crypto, plaintext);
    await runE2eBaseline(plaintext);
  }

  const aryaRuns: Record<string, number | null>[] = [];
  const baseRuns: Record<string, number | null>[] = [];

  for (let i = 0; i < runs; i++) {
    const aSt = await runAryacryptStaged(plaintext);
    const aE2e = await runE2eAryacrypt(crypto, plaintext);
    aryaRuns.push({ ...aSt, ...aE2e });

    const bSt = await runBaselineStaged(plaintext);
    const bE2e = await runE2eBaseline(plaintext);
    baseRuns.push({ ...bSt, ...bE2e });
    console.log(`    run ${i + 1}/${runs} done`);
  }

  const heapBefore = process.memoryUsage().heapUsed;
  await crypto.encrypt(plaintext, PASSWORD, {
    salt: SALT,
    nonce: NONCE,
    timestamp: 1_700_000_000,
  });
  const heapAfter = process.memoryUsage().heapUsed;

  const aryaStats = aggregate(aryaRuns, METRIC_KEYS);
  const baseStats = aggregate(baseRuns, METRIC_KEYS);

  return {
    size_bytes: size,
    size_label: label,
    runs,
    aryacrypt: aryaStats,
    baseline: baseStats,
    overhead_enc_pct_mean: overheadPct(
      aryaStats.t_total_enc.mean,
      baseStats.t_total_enc.mean
    ),
    overhead_dec_pct_mean: overheadPct(
      aryaStats.t_total_dec.mean,
      baseStats.t_total_dec.mean
    ),
    memory: {
      heap_before_bytes: heapBefore,
      heap_after_bytes: heapAfter,
      heap_delta_bytes: heapAfter - heapBefore,
    },
    raw_runs: { aryacrypt: aryaRuns, baseline: baseRuns },
  };
}

function collectEnv() {
  let pkgVersion: string | null = null;
  try {
    const require = createRequire(import.meta.url);
    pkgVersion = require("../../node-sdk/package.json").version;
  } catch {
    pkgVersion = null;
  }
  return {
    timestamp_utc: new Date().toISOString(),
    runtime: "node",
    os: platform(),
    os_release: release(),
    machine: arch(),
    cpu_model: cpus()[0]?.model ?? null,
    cpu_count: cpus().length,
    node_version: process.version,
    framework_version: FRAMEWORK_VERSION,
    package_version: pkgVersion,
    total_ram_bytes: totalmem(),
  };
}

function parseArgs(argv: string[]) {
  const quick = argv.includes("--quick");
  let runs: number | null = null;
  const runsIdx = argv.indexOf("--runs");
  if (runsIdx >= 0 && argv[runsIdx + 1]) runs = Number(argv[runsIdx + 1]);
  let sizes: number[] | null = null;
  const sizesIdx = argv.indexOf("--sizes");
  if (sizesIdx >= 0 && argv[sizesIdx + 1]) {
    sizes = argv[sizesIdx + 1]!.split(",").map((s) => Number(s.trim()));
  }
  return { quick, runs, sizes };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const sizes = args.sizes ?? (args.quick ? QUICK_SIZES : DEFAULT_SIZES);
  const crypto = new AryaCrypt();
  const env = collectEnv();

  console.log("AryaCrypt Node benchmark");
  console.log(`  framework=${FRAMEWORK_VERSION} algorithm=${ALGORITHM_ID}`);
  console.log("  disclaimer: performance only — not a security evaluation");
  console.log(`  sizes=${sizes.map(sizeLabel).join(",")}`);

  const results = [];
  for (const size of sizes) {
    const runs = args.runs ?? defaultRuns(size);
    results.push(await benchmarkSize(size, runs, crypto));
  }

  const payload = {
    schema: "aryacrypt-benchmark-v1",
    runtime: "node",
    disclaimer:
      "Performance measurements only. Not a proof of cryptographic strength. Baseline is a valid PBKDF2+AES-GCM path used to quantify preprocessing overhead.",
    environment: env,
    config: {
      password_note: "fixed Spec vector password (not logged)",
      salt_hex: SALT.toString("hex"),
      nonce_hex: NONCE.toString("hex"),
      sizes,
      framework_version: FRAMEWORK_VERSION,
    },
    results,
  };

  mkdirSync(RESULTS_DIR, { recursive: true });
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z").replace("T", "_");
  const outPath = join(RESULTS_DIR, `node_${stamp}.json`);
  const latest = join(RESULTS_DIR, "node_latest.json");
  const text = JSON.stringify(payload, null, 2);
  writeFileSync(outPath, text);
  writeFileSync(latest, text);
  console.log(`Wrote ${outPath}`);
  console.log(`Wrote ${latest}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
