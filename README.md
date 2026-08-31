# ARYACRYPT

**Cryptographic Security Framework**

A TIVRA Technology

AryaCrypt adds an **Aryabhata-inspired password preprocessing / key-generation layer**
before unmodified **PBKDF2-HMAC-SHA256** and **AES-256-GCM**. It does not replace AES.

## Overview

AryaCrypt is a research-oriented cryptographic framework and web platform for encrypting
files into a portable `.arya` container. Python and Node SDKs implement the same
[Specification v1.1.0](docs/spec/AryaCrypt_v1.1.0.md) so ciphertext is cross-compatible.

## Architecture

| Path | Role |
|------|------|
| [`python-sdk/`](python-sdk/) | Official Python package (`pip install aryacrypt`) |
| [`node-sdk/`](node-sdk/) | Official Node/TypeScript package (`npm install aryacrypt`) |
| [`backend/`](backend/) | FastAPI web API (uses the Python SDK) |
| [`frontend/`](frontend/) | React web application |
| [`docs/spec/`](docs/spec/) | Canonical specification v1.1.0 + test vectors |
| [`research/`](research/) | Background research notes |

## Security model

1. Password → Unicode NFC → Aryabhata RomanMapper stream (current algorithm path)
2. PBKDF2-HMAC-SHA256 (600,000 iterations, 16-byte salt, 32-byte key)
3. AES-256-GCM (12-byte nonce)
4. Package as `.arya` (`ARYA` + BE u32 JSON header + ciphertext)

See [docs/brand/IDENTITY.md](docs/brand/IDENTITY.md) for product positioning.

## Python SDK

```bash
pip install -e ./python-sdk
python -c "from aryacrypt import AryaCrypt; c=AryaCrypt(); print(c.decrypt(c.encrypt(b'hi','password1'),'password1'))"
```

## Node.js SDK

```bash
cd node-sdk && npm install && npm run build
```

## Web platform

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL

### Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt   # installs local ../python-sdk
# configure .env from .env.example
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Research

Research materials on Aryabhata encoding and system design live under [`research/`](research/).

## Documentation

- [AryaCrypt Specification v1.1.0](docs/spec/AryaCrypt_v1.1.0.md)
- [Test vectors](docs/spec/test-vectors/vectors.json)
- [Auth session model](docs/auth-session.md)
- [Brand identity](docs/brand/IDENTITY.md)

## Credits

- Developed by **TIVRA**
- Created by **Harsh Alkar**

## License

MIT License — Copyright (c) 2026 TIVRA

See root [`LICENSE`](LICENSE) and the SDK package licenses.
