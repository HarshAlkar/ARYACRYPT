#!/usr/bin/env python3
"""AryaCrypt research benchmark (Python) — measured timings only."""

from __future__ import annotations

import argparse
import json
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

# Allow running from repo root without installing research package
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    NONCE,
    PASSWORD,
    RAW_RESULTS_DIR,
    SALT,
    aggregate_metric_lists,
    collect_env_python,
    default_runs_for_size,
    make_plaintext,
    overhead_pct,
    should_warmup,
    size_label,
    summarize,
    throughput_mbs,
    DEFAULT_SIZES,
    QUICK_SIZES,
)

from aryacrypt import AryaCrypt, FRAMEWORK_VERSION  # noqa: E402
from aryacrypt import aes_gcm, format as arya_format, kdf, preprocess  # noqa: E402
from aryacrypt.constants import ALGORITHM_ID, LEGACY_ALGORITHM_ID  # noqa: E402


def _time_call(fn):
    t0 = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - t0


def run_aryacrypt_staged(plaintext: bytes) -> dict:
    """Stage timings for Aryabhata → PBKDF2 → AES (same crypto as SDK)."""
    _, t_pre = _time_call(lambda: preprocess.transform_password(PASSWORD))
    _, stream, _, _ = preprocess.transform_password(PASSWORD)

    key, t_kdf = _time_call(lambda: kdf.derive_key(stream, SALT))
    (ct, tag), t_enc = _time_call(lambda: aes_gcm.encrypt_bytes(key, NONCE, plaintext))
    pt, t_dec = _time_call(lambda: aes_gcm.decrypt_bytes(key, NONCE, tag, ct))
    assert pt == plaintext

    staged_sum = t_pre + t_kdf + t_enc
    return {
        "path": "aryacrypt",
        "t_preprocess": t_pre,
        "t_kdf": t_kdf,
        "t_aes_enc": t_enc,
        "t_aes_dec": t_dec,
        "t_staged_enc_sum": staged_sum,
        "preprocess_share": (t_pre / staged_sum) if staged_sum > 0 else None,
        "throughput_aes_enc_mbs": throughput_mbs(len(plaintext), t_enc),
        "throughput_aes_dec_mbs": throughput_mbs(len(plaintext), t_dec),
    }


def run_baseline_staged(plaintext: bytes) -> dict:
    """UTF-8(password) → PBKDF2 → AES (no Aryabhata)."""
    material = PASSWORD.encode("utf-8")
    key, t_kdf = _time_call(lambda: kdf.derive_key(material, SALT))
    (ct, tag), t_enc = _time_call(lambda: aes_gcm.encrypt_bytes(key, NONCE, plaintext))
    pt, t_dec = _time_call(lambda: aes_gcm.decrypt_bytes(key, NONCE, tag, ct))
    assert pt == plaintext

    return {
        "path": "baseline",
        "t_preprocess": 0.0,
        "t_kdf": t_kdf,
        "t_aes_enc": t_enc,
        "t_aes_dec": t_dec,
        "t_staged_enc_sum": t_kdf + t_enc,
        "preprocess_share": 0.0,
        "throughput_aes_enc_mbs": throughput_mbs(len(plaintext), t_enc),
        "throughput_aes_dec_mbs": throughput_mbs(len(plaintext), t_dec),
    }


def run_e2e_aryacrypt(crypto: AryaCrypt, plaintext: bytes) -> dict:
    blob, t_enc = _time_call(
        lambda: crypto.encrypt(plaintext, PASSWORD, salt=SALT, nonce=NONCE, timestamp=1700000000)
    )
    pt, t_dec = _time_call(lambda: crypto.decrypt(blob, PASSWORD))
    assert pt == plaintext
    return {
        "t_total_enc": t_enc,
        "t_total_dec": t_dec,
        "throughput_e2e_enc_mbs": throughput_mbs(len(plaintext), t_enc),
        "throughput_e2e_dec_mbs": throughput_mbs(len(plaintext), t_dec),
        "blob_bytes": len(blob),
    }


def run_e2e_baseline(plaintext: bytes) -> dict:
    """Legacy-equivalent end-to-end without calling AryaCrypt.encrypt_legacy RNG."""

    def _enc():
        key = kdf.derive_key(PASSWORD.encode("utf-8"), SALT)
        ct, tag = aes_gcm.encrypt_bytes(key, NONCE, plaintext)
        meta = arya_format.build_metadata(
            SALT, NONCE, tag, algorithm=LEGACY_ALGORITHM_ID, timestamp=1700000000
        )
        return arya_format.serialize_header(meta) + ct

    blob, t_enc = _time_call(_enc)

    def _dec():
        metadata, ciphertext = arya_format.parse_container(blob)
        salt = arya_format.decode_b64_field(metadata, "salt")
        nonce = arya_format.decode_b64_field(metadata, "nonce")
        tag = arya_format.decode_b64_field(metadata, "auth_tag")
        key = kdf.derive_key(PASSWORD.encode("utf-8"), salt)
        return aes_gcm.decrypt_bytes(key, nonce, tag, ciphertext)

    pt, t_dec = _time_call(_dec)
    assert pt == plaintext
    return {
        "t_total_enc": t_enc,
        "t_total_dec": t_dec,
        "throughput_e2e_enc_mbs": throughput_mbs(len(plaintext), t_enc),
        "throughput_e2e_dec_mbs": throughput_mbs(len(plaintext), t_dec),
        "blob_bytes": len(blob),
    }


def measure_memory_encrypt(crypto: AryaCrypt, plaintext: bytes) -> dict:
    tracemalloc.start()
    rss_before = None
    rss_after = None
    try:
        import psutil

        proc = psutil.Process()
        rss_before = proc.memory_info().rss
    except Exception:
        pass

    _ = crypto.encrypt(plaintext, PASSWORD, salt=SALT, nonce=NONCE, timestamp=1700000000)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    try:
        import psutil

        rss_after = psutil.Process().memory_info().rss
    except Exception:
        pass

    return {
        "tracemalloc_peak_bytes": peak,
        "tracemalloc_current_bytes": current,
        "rss_before_bytes": rss_before,
        "rss_after_bytes": rss_after,
        "rss_delta_bytes": (rss_after - rss_before)
        if rss_before is not None and rss_after is not None
        else None,
    }


METRIC_KEYS = [
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
]


def benchmark_size(size: int, runs: int, crypto: AryaCrypt) -> dict:
    plaintext = make_plaintext(size)
    label = size_label(size)
    print(f"  [{label}] size={size} runs={runs} ...", flush=True)

    if should_warmup(size):
        run_aryacrypt_staged(plaintext)
        run_baseline_staged(plaintext)
        run_e2e_aryacrypt(crypto, plaintext)
        run_e2e_baseline(plaintext)

    arya_runs = []
    base_runs = []
    for i in range(runs):
        a_st = run_aryacrypt_staged(plaintext)
        a_e2e = run_e2e_aryacrypt(crypto, plaintext)
        arya_runs.append({**a_st, **a_e2e})

        b_st = run_baseline_staged(plaintext)
        b_e2e = run_e2e_baseline(plaintext)
        base_runs.append({**b_st, **b_e2e})
        print(f"    run {i + 1}/{runs} done", flush=True)

    mem = measure_memory_encrypt(crypto, plaintext)

    arya_stats = aggregate_metric_lists(arya_runs, METRIC_KEYS)
    base_stats = aggregate_metric_lists(base_runs, METRIC_KEYS)

    arya_enc_mean = arya_stats["t_total_enc"]["mean"]
    base_enc_mean = base_stats["t_total_enc"]["mean"]
    arya_dec_mean = arya_stats["t_total_dec"]["mean"]
    base_dec_mean = base_stats["t_total_dec"]["mean"]

    return {
        "size_bytes": size,
        "size_label": label,
        "runs": runs,
        "aryacrypt": arya_stats,
        "baseline": base_stats,
        "overhead_enc_pct_mean": overhead_pct(arya_enc_mean, base_enc_mean),
        "overhead_dec_pct_mean": overhead_pct(arya_dec_mean, base_dec_mean),
        "memory": mem,
        "raw_runs": {
            "aryacrypt": arya_runs,
            "baseline": base_runs,
        },
    }


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="AryaCrypt Python research benchmark")
    p.add_argument("--quick", action="store_true", help="Omit 10MB and 100MB sizes")
    p.add_argument("--runs", type=int, default=None, help="Override runs per size")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=RAW_RESULTS_DIR,
        help="Directory for raw JSON output",
    )
    p.add_argument(
        "--sizes",
        type=str,
        default=None,
        help="Comma-separated sizes in bytes (overrides --quick)",
    )
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.sizes:
        sizes = tuple(int(x.strip()) for x in args.sizes.split(",") if x.strip())
    elif args.quick:
        sizes = QUICK_SIZES
    else:
        sizes = DEFAULT_SIZES

    env = collect_env_python()
    crypto = AryaCrypt()

    print("AryaCrypt Python benchmark")
    print(f"  framework={FRAMEWORK_VERSION} algorithm={ALGORITHM_ID}")
    print(f"  disclaimer: performance only — not a security evaluation")
    print(f"  sizes={[size_label(s) for s in sizes]}", flush=True)

    results = []
    for size in sizes:
        runs = args.runs if args.runs is not None else default_runs_for_size(size)
        results.append(benchmark_size(size, runs, crypto))

    payload = {
        "schema": "aryacrypt-benchmark-v1",
        "runtime": "python",
        "disclaimer": (
            "Performance measurements only. Not a proof of cryptographic strength. "
            "Baseline is a valid PBKDF2+AES-GCM path used to quantify preprocessing overhead."
        ),
        "environment": env,
        "config": {
            "password_note": "fixed Spec vector password (not logged)",
            "salt_hex": SALT.hex(),
            "nonce_hex": NONCE.hex(),
            "sizes": list(sizes),
            "framework_version": FRAMEWORK_VERSION,
        },
        "results": results,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = args.out_dir / f"python_{stamp}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    # Also write a stable pointer for report tooling
    latest = args.out_dir / "python_latest.json"
    latest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Wrote {latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
