import { pbkdf2 as pbkdf2Cb } from "node:crypto";
import { promisify } from "node:util";
import {
  KEY_LENGTH_BYTES,
  PBKDF2_ITERATIONS,
  SALT_LENGTH_BYTES,
} from "./constants.js";
import { AryaCryptError } from "./errors.js";

const pbkdf2 = promisify(pbkdf2Cb);

export async function deriveKey(
  passwordMaterial: Buffer,
  salt: Buffer,
  iterations: number = PBKDF2_ITERATIONS
): Promise<Buffer> {
  if (!Buffer.isBuffer(passwordMaterial)) {
    throw new AryaCryptError("KDF password material must be a Buffer.");
  }
  if (!Buffer.isBuffer(salt) || salt.length !== SALT_LENGTH_BYTES) {
    throw new AryaCryptError(`Salt must be exactly ${SALT_LENGTH_BYTES} bytes.`);
  }
  if (iterations < 100_000) {
    throw new AryaCryptError("PBKDF2 iterations must be at least 100000.");
  }
  return pbkdf2(passwordMaterial, salt, iterations, KEY_LENGTH_BYTES, "sha256");
}
