import type { PasswordPreprocess } from './aryabhata';
import type { AryaHeaderMeta } from './aryaContainer';

export type StepStatus = 'pending' | 'active' | 'done' | 'error';

export interface PipelineRow {
  label: string;
  value: string;
}

export interface PipelineStep {
  id: string;
  title: string;
  hint?: string;
  rows: PipelineRow[];
  status: StepStatus;
}

export interface ContainerPipeline {
  salt_hex: string;
  nonce_hex: string;
  auth_tag_hex: string;
  algorithm: string;
  framework_version?: string;
  pbkdf2_iterations?: number;
  key_length_bytes?: number;
  header_bytes: number;
  ciphertext_bytes: number;
  total_bytes: number;
}

function step(
  id: string,
  title: string,
  status: StepStatus,
  rows: PipelineRow[] = [],
  hint?: string
): PipelineStep {
  return { id, title, hint, rows, status };
}

export function buildEncryptSteps(
  prep: PasswordPreprocess,
  fileName: string,
  fileBytes: number
): PipelineStep[] {
  return [
    step('nfc', 'Unicode NFC normalize the password', 'done', [
      { label: 'NFC password', value: prep.nfcPassword },
      { label: 'note', value: prep.nfcPassword === prep.nfcPassword.normalize('NFC') ? 'already NFC' : 'normalized' },
    ]),
    step('seed', 'Turn password bytes into a numeric seed', 'done', [
      { label: 'UTF-8 bytes', value: prep.utf8Hex },
      { label: 'seed (hex)', value: prep.seedHex },
      { label: 'seed bits', value: String(prep.seedBits) },
    ]),
    step('aryabhata', 'Aryabhata / RomanMapper encode that seed', 'done', [
      { label: 'phonetic stream', value: prep.phonetic },
      { label: 'stream UTF-8', value: `${prep.streamHex}  (${prep.streamBytes} bytes)` },
    ], 'This stream — not the raw password — goes into PBKDF2'),
    step('salt', 'Generate random salt (16 bytes) and nonce (12 bytes)', 'pending', [
      { label: 'plaintext file', value: `${fileName}  (${fileBytes} bytes)` },
      { label: 'salt', value: 'waiting for server…' },
      { label: 'nonce', value: 'waiting for server…' },
    ]),
    step('pbkdf2', 'PBKDF2-HMAC-SHA256 → 32-byte AES key (600,000 iterations)', 'pending', [
      { label: 'input', value: 'Aryabhata stream + salt' },
      { label: 'AES-256 key', value: 'derived on server · never stored in the .arya file' },
    ]),
    step('aes', 'AES-256-GCM encrypt the plaintext', 'pending', [
      { label: 'ciphertext', value: 'waiting…' },
      { label: 'auth tag', value: 'waiting…' },
    ], 'GCM tag proves the file was not tampered with'),
    step('pack', 'Pack .arya container (ARYA + header length + JSON + ciphertext)', 'pending', [
      { label: 'magic', value: 'ARYA' },
      { label: 'algorithm', value: 'AryaCrypt-Aryabhata-PBKDF2-AES256GCM' },
    ]),
  ];
}

export function fillEncryptPipeline(steps: PipelineStep[], pipe: ContainerPipeline): PipelineStep[] {
  return steps.map((s) => {
    if (s.id === 'salt') {
      return {
        ...s,
        status: 'done' as const,
        rows: [
          s.rows[0],
          { label: 'salt', value: `${pipe.salt_hex}  (16 bytes)` },
          { label: 'nonce', value: `${pipe.nonce_hex}  (12 bytes)` },
        ],
      };
    }
    if (s.id === 'pbkdf2') {
      return {
        ...s,
        status: 'done' as const,
        rows: [
          { label: 'input', value: 'Aryabhata stream + salt' },
          { label: 'iterations', value: String(pipe.pbkdf2_iterations ?? 600000) },
          { label: 'AES-256 key', value: '32-byte key derived · never stored in the .arya file' },
        ],
      };
    }
    if (s.id === 'aes') {
      return {
        ...s,
        status: 'done' as const,
        rows: [
          { label: 'ciphertext', value: `${pipe.ciphertext_bytes} bytes` },
          { label: 'auth tag', value: `${pipe.auth_tag_hex}  (16 bytes)` },
        ],
      };
    }
    if (s.id === 'pack') {
      return {
        ...s,
        status: 'done' as const,
        rows: [
          { label: 'magic', value: 'ARYA' },
          { label: 'algorithm', value: pipe.algorithm },
          { label: 'header bytes', value: `${pipe.header_bytes}  (4 magic + 4 length + JSON)` },
          { label: 'ciphertext', value: `${pipe.ciphertext_bytes} bytes` },
          { label: 'total blob', value: `${pipe.total_bytes} bytes` },
        ],
      };
    }
    return { ...s, status: 'done' as const };
  });
}

export function buildDecryptSteps(prep: PasswordPreprocess, sourceLabel: string): PipelineStep[] {
  return [
    step('parse', 'Parse the .arya file', 'pending', [
      { label: 'source', value: sourceLabel },
      { label: 'magic', value: 'waiting…' },
    ]),
    step('header', 'Read salt, nonce, and auth tag from the JSON header', 'pending', [
      { label: 'salt', value: 'waiting…' },
      { label: 'nonce', value: 'waiting…' },
      { label: 'auth tag', value: 'waiting…' },
    ]),
    step('nfc', 'Unicode NFC + Aryabhata preprocess the password', 'done', [
      { label: 'NFC password', value: prep.nfcPassword },
      { label: 'phonetic stream', value: prep.phonetic },
      { label: 'seed (hex)', value: prep.seedHex },
    ]),
    step('pbkdf2', 'Rebuild the AES key (same preprocess + PBKDF2)', 'pending', [
      { label: 'input', value: 'Aryabhata stream + salt from header' },
      { label: 'AES-256 key', value: 're-derived on server · must match encrypt key' },
    ]),
    step('aes', 'AES-256-GCM decrypt + verify auth tag', 'pending', [
      { label: 'status', value: 'waiting for GCM authentication…' },
    ], 'Wrong password or a tampered file fails the tag check'),
    step('restore', 'Restore original plaintext file', 'pending', [
      { label: 'output', value: 'waiting…' },
    ]),
  ];
}

export function fillDecryptHeader(steps: PipelineStep[], meta: AryaHeaderMeta | ContainerPipeline): PipelineStep[] {
  const salt = 'saltHex' in meta ? meta.saltHex : meta.salt_hex;
  const nonce = 'nonceHex' in meta ? meta.nonceHex : meta.nonce_hex;
  const tag = 'authTagHex' in meta ? meta.authTagHex : meta.auth_tag_hex;
  const algorithm = 'algorithm' in meta ? meta.algorithm : '';
  const headerBytes = 'headerBytes' in meta ? meta.headerBytes : meta.header_bytes;
  const ct = 'ciphertextBytes' in meta ? meta.ciphertextBytes : meta.ciphertext_bytes;
  const magic = 'magic' in meta ? meta.magic : 'ARYA';

  return steps.map((s) => {
    if (s.id === 'parse') {
      return {
        ...s,
        status: 'done' as const,
        rows: [
          s.rows[0],
          { label: 'magic', value: magic },
          { label: 'algorithm', value: algorithm },
          { label: 'header', value: `${headerBytes} bytes` },
          { label: 'ciphertext', value: `${ct} bytes` },
        ],
      };
    }
    if (s.id === 'header') {
      return {
        ...s,
        status: 'done' as const,
        rows: [
          { label: 'salt', value: `${salt}  (16 bytes)` },
          { label: 'nonce', value: `${nonce}  (12 bytes)` },
          { label: 'auth tag', value: `${tag}  (16 bytes)` },
        ],
      };
    }
    return s;
  });
}

export function completeDecryptPipeline(steps: PipelineStep[], originalName: string, sizeBytes?: number): PipelineStep[] {
  return steps.map((s) => {
    if (s.id === 'restore') {
      return {
        ...s,
        status: 'done' as const,
        rows: [
          { label: 'output', value: sizeBytes != null ? `${originalName}  (${sizeBytes} bytes)` : originalName },
          { label: 'GCM tag', value: 'authenticated — plaintext matches original' },
        ],
      };
    }
    return { ...s, status: 'done' as const };
  });
}

export function activateStep(steps: PipelineStep[], id: string): PipelineStep[] {
  return steps.map((s) => {
    if (s.status === 'done' || s.status === 'error') return s;
    if (s.id === id) return { ...s, status: 'active' };
    return s;
  });
}

export function failActiveStep(steps: PipelineStep[], message: string): PipelineStep[] {
  let marked = false;
  return steps.map((s) => {
    if (!marked && (s.status === 'active' || s.status === 'pending')) {
      marked = true;
      return {
        ...s,
        status: 'error' as const,
        rows: [...s.rows, { label: 'error', value: message }],
      };
    }
    return s;
  });
}
