import { createCipheriv, createDecipheriv } from "node:crypto";
import {
  KEY_LENGTH_BYTES,
  NONCE_LENGTH_BYTES,
  TAG_LENGTH_BYTES,
} from "./constants.js";
import { AryaCryptError, AuthenticationError } from "./errors.js";

export function encryptBytes(
  key: Buffer,
  nonce: Buffer,
  plaintext: Buffer
): { ciphertext: Buffer; tag: Buffer } {
  validate(key, nonce);
  const cipher = createCipheriv("aes-256-gcm", key, nonce);
  const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const tag = cipher.getAuthTag();
  if (tag.length !== TAG_LENGTH_BYTES) {
    throw new AryaCryptError("Unexpected GCM tag length.");
  }
  return { ciphertext, tag };
}

export function decryptBytes(
  key: Buffer,
  nonce: Buffer,
  tag: Buffer,
  ciphertext: Buffer
): Buffer {
  validate(key, nonce);
  if (tag.length !== TAG_LENGTH_BYTES) {
    throw new AryaCryptError(`Auth tag must be ${TAG_LENGTH_BYTES} bytes.`);
  }
  try {
    const decipher = createDecipheriv("aes-256-gcm", key, nonce);
    decipher.setAuthTag(tag);
    return Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  } catch {
    throw new AuthenticationError(
      "Authentication failed: incorrect password or tampered ciphertext."
    );
  }
}

function validate(key: Buffer, nonce: Buffer): void {
  if (key.length !== KEY_LENGTH_BYTES) {
    throw new AryaCryptError(`AES key must be ${KEY_LENGTH_BYTES} bytes.`);
  }
  if (nonce.length !== NONCE_LENGTH_BYTES) {
    throw new AryaCryptError(`Nonce must be ${NONCE_LENGTH_BYTES} bytes.`);
  }
}
