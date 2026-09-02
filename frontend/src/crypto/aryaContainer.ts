/** Parse the public .arya header (magic + JSON). Ciphertext is not decrypted in the browser. */

export interface AryaHeaderMeta {
  magic: string;
  algorithm: string;
  frameworkVersion: string;
  saltHex: string;
  nonceHex: string;
  authTagHex: string;
  headerBytes: number;
  ciphertextBytes: number;
  totalBytes: number;
}

function b64ToHex(value: string): string {
  const bin = atob(value);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

export async function parseAryaHeader(file: File): Promise<AryaHeaderMeta> {
  const prefix = await file.slice(0, 8).arrayBuffer();
  const view = new DataView(prefix);
  const magic = new TextDecoder().decode(new Uint8Array(prefix, 0, 4));
  if (magic !== 'ARYA') {
    throw new Error("Invalid file format. Magic bytes 'ARYA' not found.");
  }
  const jsonLen = view.getUint32(4, false);
  if (jsonLen > 10240) {
    throw new Error('Unsafely massive header detected.');
  }
  const headerEnd = 8 + jsonLen;
  const jsonBuf = await file.slice(8, headerEnd).arrayBuffer();
  const metadata = JSON.parse(new TextDecoder().decode(jsonBuf)) as Record<string, string>;
  return {
    magic,
    algorithm: metadata.algorithm ?? 'AryaCrypt-Aryabhata-PBKDF2-AES256GCM',
    frameworkVersion: metadata.framework_version ?? '1.1.0',
    saltHex: b64ToHex(metadata.salt),
    nonceHex: b64ToHex(metadata.nonce),
    authTagHex: b64ToHex(metadata.auth_tag),
    headerBytes: headerEnd,
    ciphertextBytes: Math.max(0, file.size - headerEnd),
    totalBytes: file.size,
  };
}
