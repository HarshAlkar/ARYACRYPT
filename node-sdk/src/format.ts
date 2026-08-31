import {
  ALGORITHM_ID,
  CONTAINER_VERSION,
  FRAMEWORK_VERSION,
  MAGIC_BYTES,
  MAX_HEADER_LENGTH,
} from "./constants.js";
import { FormatError } from "./errors.js";

export interface AryaMetadata {
  version: number;
  framework_version: string;
  algorithm: string;
  salt: string;
  nonce: string;
  auth_tag: string;
  timestamp: number;
}

export function buildMetadata(
  salt: Buffer,
  nonce: Buffer,
  authTag: Buffer,
  opts: { algorithm?: string; timestamp?: number; version?: number } = {}
): AryaMetadata {
  return {
    version: opts.version ?? CONTAINER_VERSION,
    framework_version: FRAMEWORK_VERSION,
    algorithm: opts.algorithm ?? ALGORITHM_ID,
    salt: salt.toString("base64"),
    nonce: nonce.toString("base64"),
    auth_tag: authTag.toString("base64"),
    timestamp:
      opts.timestamp ?? Math.floor(Date.now() / 1000),
  };
}

export function serializeHeader(metadata: AryaMetadata): Buffer {
  const jsonBytes = Buffer.from(JSON.stringify(metadata), "utf8");
  const len = Buffer.alloc(4);
  len.writeUInt32BE(jsonBytes.length, 0);
  return Buffer.concat([MAGIC_BYTES, len, jsonBytes]);
}

export function parseContainer(blob: Buffer): { metadata: AryaMetadata; ciphertext: Buffer } {
  if (blob.length < 8) {
    throw new FormatError("Truncated .arya container.");
  }
  if (!blob.subarray(0, 4).equals(MAGIC_BYTES)) {
    throw new FormatError("Invalid file format. Magic bytes 'ARYA' not found.");
  }
  const headerLength = blob.readUInt32BE(4);
  if (headerLength > MAX_HEADER_LENGTH) {
    throw new FormatError(`Unsafely massive header detected (${headerLength} bytes).`);
  }
  const end = 8 + headerLength;
  if (blob.length < end) {
    throw new FormatError("Unexpected end of file while reading JSON header.");
  }
  let metadata: AryaMetadata;
  try {
    metadata = JSON.parse(blob.subarray(8, end).toString("utf8"));
  } catch {
    throw new FormatError("Invalid metadata JSON.");
  }
  return { metadata, ciphertext: blob.subarray(end) };
}

export function decodeB64Field(metadata: AryaMetadata, key: keyof AryaMetadata): Buffer {
  const value = metadata[key];
  if (typeof value !== "string" || !value) {
    throw new FormatError(`Invalid or missing metadata field '${String(key)}'.`);
  }
  if (!/^[A-Za-z0-9+/]+={0,2}$/.test(value) || value.length % 4 !== 0) {
    throw new FormatError(`Invalid Base64 in metadata field '${String(key)}'.`);
  }
  return Buffer.from(value, "base64");
}
