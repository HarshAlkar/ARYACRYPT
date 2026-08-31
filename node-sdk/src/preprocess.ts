import {
  ALGORITHM_ID,
  AVARGA_START_TENS,
  BASE_DIVISOR,
  MAX_NUMERIC_SEED_SIZE_BITS,
  MIN_PASSWORD_LENGTH,
  VARGA_MAX_VALUE,
} from "./constants.js";
import { AryaCryptError } from "./errors.js";
import { AryabhataMapping } from "./mapping.js";

export interface TransformResult {
  nfcPassword: string;
  stream: Buffer;
  seed: bigint;
  phonetic: string;
}

function bitLength(n: bigint): number {
  if (n === 0n) return 0;
  return n.toString(2).length;
}

function encodeSeed(seedIn: bigint, mapping: AryabhataMapping): string {
  let encoded = "";
  let power = 0;
  let seed = seedIn;
  const vowelCount = mapping.vowelCount;

  while (seed > 0n) {
    const remainder = Number(seed % BigInt(BASE_DIVISOR));
    seed = seed / BigInt(BASE_DIVISOR);
    const vowel = mapping.getVowelSymbol(power % vowelCount);
    if (!vowel) {
      throw new AryaCryptError(`Internal Mapping Error: No vowel for power ${power % vowelCount}.`);
    }

    if (remainder > 0 && remainder <= VARGA_MAX_VALUE) {
      const consonant = mapping.getVargaSymbol(remainder);
      if (!consonant) {
        throw new AryaCryptError(`Internal Mapping Error: Missing Varga for ${remainder}.`);
      }
      encoded = consonant + vowel + encoded;
    } else if (remainder > VARGA_MAX_VALUE) {
      const tens = Math.floor(remainder / 10) * 10;
      const units = remainder % 10;
      if (tens >= AVARGA_START_TENS) {
        const avarga = mapping.getAvargaSymbol(tens);
        if (!avarga) {
          throw new AryaCryptError(`Internal Mapping Error: Missing Avarga for ${tens}.`);
        }
        encoded = avarga + vowel + encoded;
      }
      if (units > 0) {
        const varga = mapping.getVargaSymbol(units);
        if (!varga) {
          throw new AryaCryptError(`Internal Mapping Error: Missing Varga for ${units}.`);
        }
        encoded = varga + vowel + encoded;
      }
    }
    power += 1;
  }

  return encoded;
}

export function transformPassword(password: string): TransformResult {
  if (typeof password !== "string") {
    throw new AryaCryptError("Expected password to be a string.");
  }
  // Spec: Unicode code-point length (not UTF-16 code units)
  const codePointLength = [...password].length;
  if (codePointLength < MIN_PASSWORD_LENGTH) {
    throw new AryaCryptError(
      `Password must be at least ${MIN_PASSWORD_LENGTH} characters long.`
    );
  }

  const nfcPassword = password.normalize("NFC");
  const encoded = Buffer.from(nfcPassword, "utf8");
  let seed = 0n;
  for (const byte of encoded) {
    seed = (seed << 8n) | BigInt(byte);
  }
  if (bitLength(seed) > MAX_NUMERIC_SEED_SIZE_BITS) {
    throw new AryaCryptError(
      `Generated numeric seed exceeds the safety limit of ${MAX_NUMERIC_SEED_SIZE_BITS} bits.`
    );
  }

  const mapping = new AryabhataMapping();
  const phonetic = encodeSeed(seed, mapping);
  const stream = Buffer.from(phonetic, "utf8");
  return { nfcPassword, stream, seed, phonetic };
}

export function usesAryabhata(algorithm: string | null | undefined): boolean {
  if (!algorithm) return true;
  return algorithm.includes("Aryabhata") || algorithm === ALGORITHM_ID;
}
