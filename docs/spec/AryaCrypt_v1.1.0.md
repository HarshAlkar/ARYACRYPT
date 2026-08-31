# AryaCrypt Specification v1.1.0

**Status:** Normative  
**Framework version:** `1.1.0`  
**Container version:** `1`  

AryaCrypt is a **password preprocessing / key-generation framework** that feeds a
deterministic byte stream into unmodified **PBKDF2-HMAC-SHA256** and
**AES-256-GCM**. It does **not** replace AES and does **not** claim greater
strength than AES-256-GCM itself.

There is **no standalone SHA-256 digest** of the Aryabhata stream before PBKDF2.
SHA-256 is used only as the PRF inside PBKDF2-HMAC-SHA256.

Canonical encoder: **RomanMapper** (not `AryabhataEncoder`).

---

## 1. Character normalization

1. Password must be a Unicode string.
2. Reject if `length(raw_password) < 8` (code-point length **before** NFC).
3. Normalize with **Unicode NFC**.
4. Encode NFC string as **UTF-8**.

## 2. Numeric seed

```
seed = IntegerFromBytes(UTF-8(NFC(password)), big-endian)
```

Reject if `seed.bit_length() > 4096`.

## 3. Symbol tables

### Varga (values 1–25)

`k kh g gh ng c ch j jh ny t th d dh n t th d dh n p ph b bh m`

### Avarga (tens 30…100)

| 30 | 40 | 50 | 60 | 70 | 80 | 90 | 100 |
|----|----|----|----|----|----|----|-----|
| y | r | l | v | sh | ss | s | h |

### Vowels (power mod 9)

`a i u r l e o ai au`

## 4. RomanMapper Base-100 encoding

```
phonetic = ""
power = 0
while seed > 0:
  r = seed % 100
  seed = seed // 100
  v = VOWELS[power % 9]
  if 1 <= r <= 25:
    phonetic = VARGA[r] + v + phonetic
  elif r > 25:
    tens = (r // 10) * 10
    units = r % 10
    if tens >= 30:
      phonetic = AVARGA[tens] + v + phonetic
    if units > 0:
      phonetic = VARGA[units] + v + phonetic
  # r == 0: emit nothing
  power += 1
```

Notes:

- Syllables are **prepended** (high places end up on the left).
- Remainders **26–29**: Avarga skipped; only units mapped (lossy; intentional).
- Compound example: `r=37` → readable `"chaya"` (units then tens).

## 5. Stream / PBKDF2 password bytes

```
stream_bytes = UTF-8(phonetic)
```

## 6. PBKDF2-HMAC-SHA256

| Parameter | Value |
|-----------|-------|
| PRF | HMAC-SHA256 |
| iterations | **600000** |
| dkLen | **32** |
| salt | **16** bytes CSPRNG |
| password | `stream_bytes` (Aryabhata) or UTF-8(password) (legacy) |

## 7. AES-256-GCM

| Parameter | Value |
|-----------|-------|
| key | 32 bytes from PBKDF2 |
| nonce | **12** bytes CSPRNG (never reuse with same key) |
| tag | **16** bytes |
| AAD | empty |
| ciphertext | GCM ciphertext only (tag stored in metadata) |

## 8. `.arya` container (v1)

```
[0:4]   MAGIC = "ARYA" (0x41 0x52 0x59 0x41)
[4:8]   HEADER_LEN = uint32 big-endian
[8:8+L] UTF-8 JSON metadata
[8+L:]  ciphertext
```

Max `L` on parse: **10240**.

### JSON metadata

| Field | Type | Write value |
|-------|------|-------------|
| `version` | int | `1` |
| `framework_version` | string | `"1.1.0"` |
| `algorithm` | string | see below |
| `salt` | string | standard Base64 |
| `nonce` | string | standard Base64 |
| `auth_tag` | string | standard Base64 |
| `timestamp` | int | UTC unix seconds |

**New writes algorithm:** `AryaCrypt-Aryabhata-PBKDF2-AES256GCM`  
**Legacy algorithm:** `AryaCrypt-PBKDF2-AES256GCM` → PBKDF2 password = UTF-8(password)

Detection: use Aryabhata if algorithm is missing/empty, contains `"Aryabhata"`, or equals the Aryabhata id.

## 9. Security rules

- Never log passwords, keys, or stream bytes.
- Never store plaintext passwords.
- Reject invalid GCM tags uniformly (wrong password / tamper).
- Fresh salt and nonce every encryption.

## 10. Test vectors

Canonical vectors: [`test-vectors/`](./test-vectors/). Both SDKs MUST pass them bit-for-bit.
