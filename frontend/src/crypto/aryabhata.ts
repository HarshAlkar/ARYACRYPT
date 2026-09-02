/** Client-side Aryabhata / RomanMapper preprocess (Spec v1.1.0). Display only — KDF stays on the server. */

const VARGA_CONSONANTS = [
  'k', 'kh', 'g', 'gh', 'ng',
  'c', 'ch', 'j', 'jh', 'ny',
  't', 'th', 'd', 'dh', 'n',
  't', 'th', 'd', 'dh', 'n',
  'p', 'ph', 'b', 'bh', 'm',
] as const;

const AVARGA_CONSONANTS = ['y', 'r', 'l', 'v', 'sh', 'ss', 's', 'h'] as const;
const VOWEL_MULTIPLIERS = ['a', 'i', 'u', 'r', 'l', 'e', 'o', 'ai', 'au'] as const;

const BASE_DIVISOR = 100;
const VARGA_MAX_VALUE = 25;
const AVARGA_START_TENS = 30;
const MIN_PASSWORD_LENGTH = 8;

export interface PasswordPreprocess {
  nfcPassword: string;
  utf8Hex: string;
  seedHex: string;
  seedBits: number;
  phonetic: string;
  streamHex: string;
  streamBytes: number;
}

function bytesToBigInt(bytes: Uint8Array): bigint {
  let n = 0n;
  for (const b of bytes) {
    n = (n << 8n) + BigInt(b);
  }
  return n;
}

function encodeSeed(seedIn: bigint): string {
  const varga = new Map<number, string>();
  VARGA_CONSONANTS.forEach((symbol, index) => varga.set(index + 1, symbol));
  const avarga = new Map<number, string>();
  let tens = AVARGA_START_TENS;
  for (const symbol of AVARGA_CONSONANTS) {
    avarga.set(tens, symbol);
    tens += 10;
  }

  let encoded = '';
  let power = 0;
  let seed = seedIn;
  const vowelCount = VOWEL_MULTIPLIERS.length;

  while (seed > 0n) {
    const remainder = Number(seed % BigInt(BASE_DIVISOR));
    seed = seed / BigInt(BASE_DIVISOR);
    const vowel = VOWEL_MULTIPLIERS[power % vowelCount];

    if (remainder > 0 && remainder <= VARGA_MAX_VALUE) {
      encoded = (varga.get(remainder) ?? '') + vowel + encoded;
    } else if (remainder > VARGA_MAX_VALUE) {
      const t = Math.floor(remainder / 10) * 10;
      const units = remainder % 10;
      if (t >= AVARGA_START_TENS) {
        encoded = (avarga.get(t) ?? '') + vowel + encoded;
      }
      if (units > 0) {
        encoded = (varga.get(units) ?? '') + vowel + encoded;
      }
    }
    power += 1;
  }
  return encoded;
}

export function transformPassword(password: string): PasswordPreprocess {
  if ([...password].length < MIN_PASSWORD_LENGTH) {
    throw new Error(`Password must be at least ${MIN_PASSWORD_LENGTH} characters.`);
  }
  const nfcPassword = password.normalize('NFC');
  const utf8 = new TextEncoder().encode(nfcPassword);
  const seed = bytesToBigInt(utf8);
  const phonetic = encodeSeed(seed);
  const stream = new TextEncoder().encode(phonetic);
  return {
    nfcPassword,
    utf8Hex: bufferToHex(utf8),
    seedHex: seed.toString(16),
    seedBits: seed === 0n ? 0 : seed.toString(2).length,
    phonetic,
    streamHex: bufferToHex(stream),
    streamBytes: stream.length,
  };
}

export function bufferToHex(data: Uint8Array): string {
  return Array.from(data, (b) => b.toString(16).padStart(2, '0')).join('');
}
