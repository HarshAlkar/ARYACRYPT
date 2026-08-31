# ARYACRYPT

**A TIVRA Cryptographic Security Framework**

Official Python SDK for AryaCrypt (spec **v1.1.0**).

AryaCrypt adds an Aryabhata-inspired **password preprocessing** layer before
unmodified **PBKDF2-HMAC-SHA256** and **AES-256-GCM**. It does not replace AES.

Developed by **TIVRA** · Created by **Harsh Alkar**

## Installation

```bash
pip install aryacrypt
```

For local development from this monorepo:

```bash
pip install -e ./python-sdk
```

## Quick start

```python
from aryacrypt import AryaCrypt

crypto = AryaCrypt()
blob = crypto.encrypt(b"hello aryacrypt", "password1")
plain = crypto.decrypt(blob, "password1")
assert plain == b"hello aryacrypt"
```

Cross-compatible with the Node.js `aryacrypt` package (same `.arya` format).

## Security notes

- Minimum password length: 8 Unicode code points
- PBKDF2-HMAC-SHA256: 600,000 iterations; 16-byte salt; 32-byte key
- AES-256-GCM with a 12-byte nonce
- Do not reuse salts or nonces across independent encryptions

## Documentation

- Spec: `docs/spec/AryaCrypt_v1.1.0.md` (monorepo)
- Test vectors: `docs/spec/test-vectors/vectors.json`
- Brand identity: `docs/brand/IDENTITY.md`

## License

MIT — Copyright (c) 2026 TIVRA
