export const VARGA_CONSONANTS = [
  "k", "kh", "g", "gh", "ng",
  "c", "ch", "j", "jh", "ny",
  "t", "th", "d", "dh", "n",
  "t", "th", "d", "dh", "n",
  "p", "ph", "b", "bh", "m",
] as const;

export const AVARGA_CONSONANTS = [
  "y", "r", "l", "v", "sh", "ss", "s", "h",
] as const;

export const VOWEL_MULTIPLIERS = [
  "a", "i", "u", "r", "l", "e", "o", "ai", "au",
] as const;

export const BASE_DIVISOR = 100;
export const VARGA_MAX_VALUE = 25;
export const AVARGA_START_TENS = 30;
export const MAX_NUMERIC_SEED_SIZE_BITS = 4096;
export const MIN_PASSWORD_LENGTH = 8;

export const SALT_LENGTH_BYTES = 16;
export const NONCE_LENGTH_BYTES = 12;
export const KEY_LENGTH_BYTES = 32;
export const TAG_LENGTH_BYTES = 16;
export const PBKDF2_ITERATIONS = 600_000;

export const MAGIC_BYTES = Buffer.from("ARYA", "utf8");
export const FRAMEWORK_VERSION = "1.1.0";
export const CONTAINER_VERSION = 1;
export const ALGORITHM_ID = "AryaCrypt-Aryabhata-PBKDF2-AES256GCM";
export const LEGACY_ALGORITHM_ID = "AryaCrypt-PBKDF2-AES256GCM";
export const MAX_HEADER_LENGTH = 10240;
export const CHUNK_SIZE = 64 * 1024;
