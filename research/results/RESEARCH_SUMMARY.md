# AryaCrypt Research Summary

**Product:** AryaCrypt (Specification v1.1.0)  
**Organization framing:** A TIVRA technology  
**Document type:** Performance and methodology summary for project report / viva  
**Evidence basis:** Full measured benchmark suite (`research/benchmarks/results/*_latest.json`)

---

## 1. Research objective

To quantify the **computational cost** of AryaCrypt’s Aryabhata-inspired password preprocessing (RomanMapper) relative to an otherwise identical pipeline that derives keys from the UTF-8 password bytes alone, when both use **PBKDF2-HMAC-SHA256 (600,000 iterations)** and **AES-256-GCM**.

Secondary objectives: document how cost scales with plaintext size, how PBKDF2 dominates runtime, and how memory grows for in-memory encryption—without asserting cryptographic superiority from timings.

---

## 2. Methodology

- **Implementation under test:** Official Python and Node SDKs aligned to Spec v1.1.0 (no algorithm changes for this study).  
- **Baseline:** UTF-8(password) → PBKDF2 → AES-256-GCM.  
- **AryaCrypt path:** Password → RomanMapper stream → PBKDF2 → AES-256-GCM (plus end-to-end `.arya` serialize/parse where applicable).  
- **Controls:** Fixed Spec test-vector salt/nonce; deterministic seeded plaintext; staged and end-to-end timers; mean/median/min/max/stdev across repeats.  
- **Reporting:** JSON/CSV/Markdown aggregates and graphs generated only from measured files (`generate_report.py`).

---

## 3. Experiment design

| Factor | Levels |
|--------|--------|
| File size | 1 KiB, 100 KiB, 1 MiB, 10 MiB, 100 MiB |
| Repeats | 10 / 10 / 10 / 5 / 3 |
| Runtimes | Python 3.13.7; Node.js v22.19.0 (reported separately) |
| Host | Windows; 16 logical CPUs; ≈16 GiB RAM |

Environment metadata (OS, CPU count, library versions) is stored beside each raw JSON result.

---

## 4. Key measured findings

1. **PBKDF2 dominates** staged encryption time at small and medium sizes (≈99.6–99.97% on Python for ≤1 MiB; still ≈66–80% at 100 MiB depending on runtime).  
2. **RomanMapper preprocessing is sub-millisecond** (~0.08–0.14 ms) and a **negligible share** of staged encrypt time (≪ 1%).  
3. **End-to-end latency is nearly flat** from 1 KiB through ~10 MiB because the fixed KDF cost overshadows AES; **100 MiB** shows a clear increase as AES time becomes material.  
4. **End-to-end overhead vs baseline** is small and often within run-to-run noise (typically on the order of a few percent or less). The data do **not** support a claim that AryaCrypt is systematically faster.  
5. **AES throughput** for large buffers is hundreds of MB/s on this host; tiny-file “MB/s” figures are not meaningful bulk metrics.  
6. **Python memory peaks** scale approximately with payload size for in-memory encrypt; Node heap deltas are noisy/approximate.

---

## 5. Interpretation

AryaCrypt’s distinctive research contribution in this stack is **linguistic / historical diffusion of password material before a standard KDF**, not a replacement for AES-GCM. Performance results show that, under Spec v1.1.0 parameters, that preprocessing step is **cheap relative to intentional KDF hardness**. System designers should budget primarily for PBKDF2 (and for large files, AES and memory), not for RomanMapper.

---

## 6. Limitations

See [`LIMITATIONS.md`](LIMITATIONS.md). In brief: machine-specific timings; Python≠Node comparability; approximate memory; performance is not security; no independent cryptanalysis claimed; Aryabhata is preprocessing, not a new cipher.

---

## 7. Conclusion

Under reproducible full-suite measurements on the documented test host, **AryaCrypt v1.1.0 adds negligible runtime overhead** from Aryabhata/RomanMapper preprocessing compared with a UTF-8→PBKDF2→AES-256-GCM baseline, because **PBKDF2-HMAC-SHA256 (600k)** dominates. Large-file cost growth is explained by AES work and buffer memory, not by preprocessing.

These conclusions are **performance findings only** and are suitable as experimental support in a project report or viva when paired with the stated limitations and the Spec’s accurate cryptographic description.

---

## 8. Artefacts

| Path | Role |
|------|------|
| `research/benchmarks/results/python_latest.json` | Raw Python full run |
| `research/benchmarks/results/node_latest.json` | Raw Node full run |
| `research/results/benchmark_report.{json,csv,md}` | Aggregates |
| `research/results/graph_*.png` | Figures from measured data |
| `research/results/PERFORMANCE_ANALYSIS.md` | Detailed discussion |
| `research/results/LIMITATIONS.md` | Limitations |
| `research/results/RESEARCH_SUMMARY.md` | This summary |
