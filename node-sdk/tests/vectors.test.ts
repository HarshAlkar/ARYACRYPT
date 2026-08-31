import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";
import {
  AryaCrypt,
  AuthenticationError,
  FormatError,
  transformPassword,
} from "../src/index.ts";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const vectorsPath = join(root, "docs", "spec", "test-vectors", "vectors.json");
const doc = JSON.parse(readFileSync(vectorsPath, "utf8"));

test("preprocess matches vectors", () => {
  for (const item of doc.preprocess) {
    const r = transformPassword(item.password);
    assert.equal(r.nfcPassword, item.nfc_password);
    assert.equal(r.phonetic, item.phonetic);
    assert.equal(r.stream.toString("hex"), item.stream_hex);
    assert.equal(r.seed.toString(16), item.seed_hex);
  }
});

test("encrypt vectors bit-exact", async () => {
  const crypto = new AryaCrypt();
  for (const v of doc.vectors) {
    const salt = Buffer.from(v.salt_hex, "hex");
    const nonce = Buffer.from(v.nonce_hex, "hex");
    const plaintext = Buffer.from(v.plaintext_hex, "hex");
    const blob = v.legacy
      ? await crypto.encryptLegacy(plaintext, v.password, {
          salt,
          nonce,
          timestamp: v.timestamp,
        })
      : await crypto.encrypt(plaintext, v.password, {
          salt,
          nonce,
          timestamp: v.timestamp,
        });
    assert.equal(Buffer.from(blob).toString("hex"), v.arya_blob_hex);
    const plain = await crypto.decrypt(blob, v.password);
    assert.deepEqual(Buffer.from(plain), plaintext);
  }
});

test("wrong password", async () => {
  const crypto = new AryaCrypt();
  const v = doc.vectors[0];
  const blob = Buffer.from(v.arya_blob_hex, "hex");
  await assert.rejects(
    () => crypto.decrypt(blob, doc.negatives.wrong_password),
    (err: unknown) => err instanceof AuthenticationError
  );
});

test("tampered ciphertext", async () => {
  const crypto = new AryaCrypt();
  const blob = Buffer.from(doc.negatives.tampered_blob_hex, "hex");
  await assert.rejects(
    () => crypto.decrypt(blob, doc.vectors[0].password),
    (err: unknown) => err instanceof AuthenticationError
  );
});

test("short password", async () => {
  const crypto = new AryaCrypt();
  await assert.rejects(() => crypto.encrypt(Buffer.from("x"), "short"));
});

test("bad magic", async () => {
  const crypto = new AryaCrypt();
  await assert.rejects(
    () => crypto.decrypt(Buffer.from("NOTA" + "\0".repeat(20)), "password1"),
    (err: unknown) => err instanceof FormatError
  );
});
