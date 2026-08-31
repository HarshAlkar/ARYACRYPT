import { randomBytes } from "node:crypto";
import * as aesGcm from "./aesGcm.js";
import {
  ALGORITHM_ID,
  LEGACY_ALGORITHM_ID,
  MIN_PASSWORD_LENGTH,
  NONCE_LENGTH_BYTES,
  SALT_LENGTH_BYTES,
} from "./constants.js";
import { AryaCryptError } from "./errors.js";
import * as aryaFormat from "./format.js";
import * as kdf from "./kdf.js";
import * as preprocess from "./preprocess.js";

export interface EncryptOptions {
  salt?: Buffer;
  nonce?: Buffer;
  timestamp?: number;
}

export class AryaCrypt {
  async encrypt(
    data: Uint8Array,
    password: string,
    options: EncryptOptions = {}
  ): Promise<Uint8Array> {
    const plaintext = Buffer.from(data);
    const { stream } = preprocess.transformPassword(password);
    const salt = options.salt ?? randomBytes(SALT_LENGTH_BYTES);
    const nonce = options.nonce ?? randomBytes(NONCE_LENGTH_BYTES);
    if (salt.length !== SALT_LENGTH_BYTES) {
      throw new AryaCryptError(`salt must be ${SALT_LENGTH_BYTES} bytes.`);
    }
    if (nonce.length !== NONCE_LENGTH_BYTES) {
      throw new AryaCryptError(`nonce must be ${NONCE_LENGTH_BYTES} bytes.`);
    }

    const key = await kdf.deriveKey(stream, salt);
    const { ciphertext, tag } = aesGcm.encryptBytes(key, nonce, plaintext);
    const meta = aryaFormat.buildMetadata(salt, nonce, tag, {
      algorithm: ALGORITHM_ID,
      timestamp: options.timestamp,
    });
    return Buffer.concat([aryaFormat.serializeHeader(meta), ciphertext]);
  }

  async decrypt(encrypted: Uint8Array, password: string): Promise<Uint8Array> {
    const blob = Buffer.from(encrypted);
    const { metadata, ciphertext } = aryaFormat.parseContainer(blob);
    const salt = aryaFormat.decodeB64Field(metadata, "salt");
    const nonce = aryaFormat.decodeB64Field(metadata, "nonce");
    const tag = aryaFormat.decodeB64Field(metadata, "auth_tag");
    if (salt.length !== SALT_LENGTH_BYTES) {
      throw new AryaCryptError(`salt must decode to ${SALT_LENGTH_BYTES} bytes.`);
    }
    if (nonce.length !== NONCE_LENGTH_BYTES) {
      throw new AryaCryptError(`nonce must decode to ${NONCE_LENGTH_BYTES} bytes.`);
    }
    const algorithm = metadata.algorithm ?? ALGORITHM_ID;

    let material: Buffer;
    if (preprocess.usesAryabhata(algorithm)) {
      material = preprocess.transformPassword(password).stream;
    } else {
      material = Buffer.from(password, "utf8");
    }

    const key = await kdf.deriveKey(material, salt);
    return aesGcm.decryptBytes(key, nonce, tag, ciphertext);
  }

  async encryptLegacy(
    data: Uint8Array,
    password: string,
    options: EncryptOptions = {}
  ): Promise<Uint8Array> {
    if (typeof password !== "string" || [...password].length < MIN_PASSWORD_LENGTH) {
      throw new AryaCryptError(
        `Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`
      );
    }
    const plaintext = Buffer.from(data);
    const salt = options.salt ?? randomBytes(SALT_LENGTH_BYTES);
    const nonce = options.nonce ?? randomBytes(NONCE_LENGTH_BYTES);
    if (salt.length !== SALT_LENGTH_BYTES) {
      throw new AryaCryptError(`salt must be ${SALT_LENGTH_BYTES} bytes.`);
    }
    if (nonce.length !== NONCE_LENGTH_BYTES) {
      throw new AryaCryptError(`nonce must be ${NONCE_LENGTH_BYTES} bytes.`);
    }
    const key = await kdf.deriveKey(Buffer.from(password, "utf8"), salt);
    const { ciphertext, tag } = aesGcm.encryptBytes(key, nonce, plaintext);
    const meta = aryaFormat.buildMetadata(salt, nonce, tag, {
      algorithm: LEGACY_ALGORITHM_ID,
      timestamp: options.timestamp,
    });
    return Buffer.concat([aryaFormat.serializeHeader(meta), ciphertext]);
  }
}
