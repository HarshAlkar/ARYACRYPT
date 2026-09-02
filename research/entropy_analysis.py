"""Shannon / source entropy of AryaCrypt password preprocessing.

Aryabhata mapping is deterministic: it does not create new secret bits.
This script measures byte-distribution (Shannon) entropy so you can compare
password UTF-8 vs the phonetic stream vs AES-GCM ciphertext.

Run from repo root (venv with aryacrypt installed):

    python research/entropy_analysis.py
    python research/entropy_analysis.py password1
    python research/entropy_analysis.py password1 "hello Teammmm"
"""

from __future__ import annotations

import math
import os
import sys
from collections import Counter

from aryacrypt import AryaCrypt
from aryacrypt.aes_gcm import encrypt_bytes
from aryacrypt.kdf import derive_key
from aryacrypt.preprocess import transform_password


def shannon_bits_per_symbol(data: bytes) -> float:
    """H = -sum p_i log2(p_i) over observed byte values (0..8 bits/byte)."""
    if not data:
        return 0.0
    n = len(data)
    counts = Counter(data)
    h = 0.0
    for c in counts.values():
        p = c / n
        h -= p * math.log2(p)
    return h


def report_bytes(label: str, data: bytes) -> dict:
    h = shannon_bits_per_symbol(data)
    unique = len(set(data))
    total = h * len(data)
    print(f"    {label}")
    print(f"      length           : {len(data)} bytes")
    print(f"      unique byte vals : {unique} / 256")
    print(f"      Shannon H        : {h:.4f} bits/byte  (max 8.0000 if uniform)")
    print(f"      total H * n      : {total:.2f} bits")
    return {"h_per_byte": h, "total_bits": total, "n": len(data), "unique": unique}


def charset_guess_entropy(password: str) -> tuple[int, float]:
    """Rough password source entropy: L * log2(|alphabet guess|)."""
    has_lower = any("a" <= c <= "z" for c in password)
    has_upper = any("A" <= c <= "Z" for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_other = any(not c.isalnum() for c in password)
    size = 0
    if has_lower:
        size += 26
    if has_upper:
        size += 26
    if has_digit:
        size += 10
    if has_other:
        size += 33
    if size == 0:
        size = 1
    bits = len(password) * math.log2(size)
    return size, bits


def main() -> None:
    password = sys.argv[1] if len(sys.argv) > 1 else "password1"
    plaintext = (sys.argv[2] if len(sys.argv) > 2 else "hello Teammmm").encode("utf-8")

    print()
    print("=" * 72)
    print("  ARYACRYPT ENTROPY ANALYSIS")
    print("=" * 72)
    print("    Formula : H = -sum p_i * log2(p_i)   (Shannon, bits per byte)")
    print("    Note    : Aryabhata is 1-way deterministic. It does NOT add")
    print("              secret bits. H(stream) cannot exceed H(password).")
    print()

    nfc, stream, seed, phonetic = transform_password(password)
    pwd_bytes = nfc.encode("utf-8")
    alphabet, guess_bits = charset_guess_entropy(nfc)

    print("[1] Password source entropy (guessing, not Shannon)")
    print("-" * 72)
    print(f"    password           : {nfc!r}")
    print(f"    length             : {len(nfc)} characters")
    print(f"    guessed alphabet   : {alphabet} symbols")
    print(f"    ~ log2(|A|^L)      : {guess_bits:.2f} bits")
    print("    (this is the real secret: attacker must guess the password)")

    print()
    print("[2] Shannon entropy of password UTF-8 bytes")
    print("-" * 72)
    pwd_stats = report_bytes("password UTF-8", pwd_bytes)
    print(f"    seed (hex)         : {format(seed, 'x')}")

    print()
    print("[3] Shannon entropy of Aryabhata phonetic stream")
    print("-" * 72)
    print(f"    phonetic           : {phonetic}")
    stream_stats = report_bytes("Aryabhata stream UTF-8", stream)
    delta = stream_stats["h_per_byte"] - pwd_stats["h_per_byte"]
    print(f"    H_stream - H_pwd   : {delta:+.4f} bits/byte")
    print("    mapping spreads bytes over more letter symbols, so H/byte")
    print("    can go UP, but the secret is still the same password.")

    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(stream, salt)
    ciphertext, tag = encrypt_bytes(key, nonce, plaintext)
    blob = AryaCrypt().encrypt(plaintext, password)

    print()
    print("[4] After PBKDF2 + AES-256-GCM (should look near-uniform)")
    print("-" * 72)
    report_bytes("AES-256 key (32 bytes)", key)
    report_bytes("GCM ciphertext", ciphertext)
    report_bytes("full .arya blob", blob)
    print("    32-byte key Shannon is a small-sample estimate; do not treat")
    print("    8.00 bits/byte here as a security proof. GCM ciphertext of a")
    print("    longer file should sit close to 8 bits/byte.")

    print()
    print("=" * 72)
    print("  HOW TO READ THIS")
    print("=" * 72)
    print("    Password bits  -> how hard to guess (security of the secret)")
    print("    Shannon H/byte -> how mixed the byte histogram looks")
    print("    Aryabhata      -> changes the histogram, not the secret size")
    print("    AES-GCM        -> ciphertext should look random (~8 bits/byte)")
    print()


if __name__ == "__main__":
    main()
