# ARYACRYPT

**A TIVRA Cryptographic Security Framework**

Official Node.js / TypeScript SDK for AryaCrypt (spec **v1.1.0**).

Developed by **TIVRA** · Created by **Harsh Alkar**

## Installation

```bash
npm install aryacrypt
```

## Quick start

```ts
import { AryaCrypt } from "aryacrypt";

const crypto = new AryaCrypt();
const blob = await crypto.encrypt(Buffer.from("hello aryacrypt"), "password1");
const plain = await crypto.decrypt(blob, "password1");
```

Cross-compatible with the Python `aryacrypt` package (same `.arya` format).

## Security notes

- Minimum password length: 8 Unicode code points
- PBKDF2-HMAC-SHA256: 600,000 iterations; 16-byte salt; 32-byte key
- AES-256-GCM with a 12-byte nonce

## Documentation

- Spec: `docs/spec/AryaCrypt_v1.1.0.md` (monorepo)
- Test vectors: `docs/spec/test-vectors/vectors.json`
- Brand identity: `docs/brand/IDENTITY.md`

## License

MIT — Copyright (c) 2026 TIVRA
