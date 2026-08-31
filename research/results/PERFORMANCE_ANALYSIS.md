# AryaCrypt Performance Analysis

**Source:** Measured outputs in `research/benchmarks/results/python_latest.json` and `node_latest.json`  
**Framework:** AryaCrypt Specification v1.1.0  
**Disclaimer:** This document discusses **runtime performance only**. It does **not** evaluate or imply cryptographic strength.

---

## 1. Experiment context

Two pipelines were timed with identical fixed salt, nonce, and deterministic plaintext:

| Path | Pipeline |
|------|----------|
| Baseline | UTF-8(password) → PBKDF2-HMAC-SHA256 (600,000 iterations) → AES-256-GCM |
| AryaCrypt | RomanMapper / Aryabhata preprocess → PBKDF2-HMAC-SHA256 (600,000) → AES-256-GCM |

Sizes: 1 KiB, 100 KiB, 1 MiB, 10 MiB, 100 MiB.  
Repeats: 10 (≤1 MiB), 5 (10 MiB), 3 (100 MiB).

Python and Node results are reported **separately**. Cross-runtime wall-clock comparison is not used as an equality claim.

---

## 2. Test environment (this run)

| Item | Value |
|------|-------|
| OS | Windows (build family 10/11) |
| CPU | 16 logical processors (AMD Ryzen 7 5800H class) |
| RAM | ≈ 15.9 GiB |
| Python | 3.13.7 |
| Node.js | v22.19.0 |
| cryptography (Python) | 45.0.7 |
| AryaCrypt framework | 1.1.0 |

---

## 3. Scaling of encryption and decryption time

### Python (mean end-to-end)

| Size | AryaCrypt enc (s) | Baseline enc (s) | AryaCrypt dec (s) | Baseline dec (s) |
|------|-------------------:|-----------------:|-------------------:|-----------------:|
| 1 KB | 0.818 | 0.816 | ≈0.81 | ≈0.81 |
| 100 KB | 0.837 | 0.824 | ≈0.83 | ≈0.83 |
| 1 MB | 0.821 | 0.835 | ≈0.83 | ≈0.82 |
| 10 MB | 0.872 | 0.823 | ≈0.86 | ≈0.87 |
| 100 MB | 1.344 | 1.275 | ≈1.33 | ≈1.32 |

**Observation:** For sizes up to about 10 MiB, end-to-end time is nearly flat (~0.8–0.9 s). That pattern matches a **fixed PBKDF2 cost** plus a small AES cost. Only at **100 MiB** does AES become large enough (~0.43 s mean AES encrypt on Python) that total time clearly rises.

Decryption follows the same structure: one PBKDF2 derivation per decrypt plus AES-GCM decrypt proportional to ciphertext size.

### Node.js (mean end-to-end)

| Size | AryaCrypt enc (s) | Baseline enc (s) |
|------|-------------------:|-----------------:|
| 1 KB | 0.646 | 0.651 |
| 100 KB | 0.631 | 0.633 |
| 1 MB | 0.656 | 0.640 |
| 10 MB | 0.667 | 0.664 |
| 100 MB | 0.881 | 0.870 |

Node shows the same qualitative shape (PBKDF2-dominated plateau, rise at 100 MiB) with a lower PBKDF2 wall time on this machine (~0.63 s KDF mean). Absolute Node vs Python seconds must **not** be treated as a like-for-like runtime contest.

---

## 4. PBKDF2 contribution

Staged AryaCrypt encrypt sum ≈ preprocess + KDF + AES encrypt.

| Size | Python KDF mean (s) | PBKDF2 share of staged enc | Node KDF mean (s) | PBKDF2 share |
|------|--------------------:|---------------------------:|------------------:|-------------:|
| 1 KB | 0.813 | **99.97%** | 0.650 | **99.95%** |
| 100 KB | 0.848 | **99.96%** | 0.638 | **99.90%** |
| 1 MB | 0.836 | **99.61%** | 0.625 | **99.63%** |
| 10 MB | 0.807 | **94.80%** | 0.627 | **97.27%** |
| 100 MB | 0.828 | **65.62%** | 0.633 | **79.68%** |

**Finding:** At small and medium sizes, PBKDF2 accounts for essentially all staged encrypt time. Even at 100 MiB, PBKDF2 still dominates on both runtimes, though AES’s share grows.

This is expected: 600,000 PBKDF2-HMAC-SHA256 iterations are intentionally expensive and **independent of plaintext length**.

---

## 5. Aryabhata / RomanMapper preprocessing overhead

| Runtime | Preprocess mean (approx.) | Preprocess share of staged enc |
|---------|---------------------------:|-------------------------------:|
| Python | 0.08–0.09 ms | ≈ 0.007–0.01% |
| Node | 0.11–0.14 ms | ≈ 0.02% |

End-to-end encrypt overhead percentage (AryaCrypt vs baseline means) on Python ranged roughly from about **−1.6% to +5.9%** across sizes; on Node roughly **−0.8% to +2.5%** (with one decrypt point higher at 100 MiB). Values near zero with mixed sign are consistent with **measurement noise** around a large shared PBKDF2 cost, not a large fixed Aryabhata tax.

**Interpretation:** On this hardware, RomanMapper preprocessing is **negligible** relative to PBKDF2. It does not materially change end-to-end latency for the tested sizes.

Absolute overhead in seconds is on the order of the preprocess duration itself (sub-millisecond), while PBKDF2 is hundreds of milliseconds.

---

## 6. Throughput

AES-stage encrypt throughput (MB/s, mean) increases once payloads leave the sub-millisecond AES regime:

- **Python:** ~6.6 MB/s at 1 KiB (timer resolution / fixed overhead dominated) → ~240–390 MB/s for larger sizes in this run.  
- **Node:** similar small-file artifact; larger sizes measured hundreds of MB/s AES throughput on this host.

End-to-end throughput remains low for small files because **PBKDF2 is paid once per encrypt**, so MB/s for 1 KiB is not a meaningful bulk-throughput figure.

---

## 7. Memory behaviour

**Python (`tracemalloc` peak during one encrypt):**

| Size | Peak (approx.) |
|------|----------------:|
| 1 KB | ~4 KiB |
| 100 KB | ~202 KiB |
| 1 MB | ~2.0 MiB |
| 10 MB | ~20 MiB |
| 100 MB | ~200 MiB |

Peak scales roughly with payload size for the in-memory encrypt path (plaintext/ciphertext buffers). RSS deltas, where recorded, also grew with size (approximate OS-level measure).

**Node:** heap deltas around a single encrypt were small or slightly negative (GC noise). Treat Node heap deltas as **approximate**, not precise RSS accounting.

---

## 8. Small-file vs large-file behaviour

| Regime | Dominant cost | User-visible effect |
|--------|---------------|---------------------|
| Small (≤1 MiB) | PBKDF2 | Latency ≈ constant (~KDF time) |
| Large (100 MiB) | PBKDF2 + AES | Latency ≈ KDF + Θ(size) AES |

Preprocessing does not change this regime split in the measured data.

---

## 9. Variance / noise

- Multiple repeats reduce noise; stdev is recorded in JSON/CSV aggregates.  
- Overhead percentages near ± a few percent are **not** strong evidence that AryaCrypt is faster or slower end-to-end; both paths share the same expensive KDF.  
- Timer granularity and OS scheduling affect microsecond-scale preprocess and tiny AES jobs.

---

## 10. Runtime-specific notes

### Python
- `cryptography` AES-GCM and OpenSSL-backed PBKDF2.  
- Clear linear growth of `tracemalloc` peak with file size.  
- At 100 MiB, staged AES (~0.43 s) becomes visible beside ~0.83 s KDF.

### Node
- `node:crypto` PBKDF2/AES on this machine completed KDF faster than Python in wall time (implementation/runtime difference—not a security claim).  
- Same structural conclusion: preprocess ≪ PBKDF2; AES grows with size.

---

## 11. Baseline comparison (summary)

| Quantity | Measured character |
|----------|--------------------|
| Absolute preprocess cost | Sub-millisecond |
| % of staged encrypt | ≪ 1% |
| End-to-end vs baseline | Within noise / few percent |
| Why PBKDF2 dominates | Fixed 600k iterations, size-independent |

The baseline is a **valid** PBKDF2+AES-GCM construction. The experiment only quantifies the extra deterministic preprocessing step.

---

## 12. What these results do *not* show

- They do **not** prove stronger (or weaker) cryptography.  
- They do **not** replace cryptanalysis.  
- They do **not** justify advertising “faster encryption” as a security benefit.
