# AryaCrypt Research Benchmarks

Performance measurements for **AryaCrypt Specification v1.1.0**.

These scripts do **not** modify the SDK, Spec, or production application.
Timings are **performance data only** — they are not evidence of cryptographic strength.

## What is measured

| Path | Pipeline |
|------|----------|
| **Baseline** | UTF-8(password) → PBKDF2-HMAC-SHA256 (600k) → AES-256-GCM |
| **AryaCrypt** | Password → RomanMapper/Aryabhata preprocess → PBKDF2 → AES-256-GCM |

Also timed: preprocessing alone, KDF alone, AES encrypt/decrypt, end-to-end `AryaCrypt.encrypt` / `decrypt`, throughput (MB/s), and approximate memory.

## Deterministic inputs

- Password: `password1`
- Salt / nonce: fixed bytes from Spec test vector `basic-ascii`
- Plaintext: seeded PRNG fill for 1 KB, 100 KB, 1 MB, 10 MB, 100 MB

## One-command reproduce (Python)

From the repository root:

```bash
pip install -e ./python-sdk
pip install -r research/benchmarks/requirements.txt
python research/benchmarks/benchmark_python.py
python research/benchmarks/generate_report.py
```

Quick smoke (skips 10 MB and 100 MB):

```bash
python research/benchmarks/benchmark_python.py --quick
python research/benchmarks/generate_report.py
```

## Node.js counterpart

```bash
cd node-sdk && npm install
npx tsx ../research/benchmarks/benchmark_node.ts
# optional: --quick
npx tsx ../research/benchmarks/benchmark_node.ts --quick
```

Then regenerate the report (picks up latest JSON under `results/`):

```bash
python research/benchmarks/generate_report.py
```

## Outputs

| Location | Contents |
|----------|----------|
| `research/benchmarks/results/*.json` | Raw timed runs + environment |
| `research/results/benchmark_report.{json,csv,md}` | Aggregated tables |
| `research/results/*.png` | Graphs from measured data |

## Flags

- `--quick` — sizes ≤ 1 MB only
- `--runs N` — override iteration count
- `--out-dir PATH` — raw JSON directory (default: `research/benchmarks/results`)

## Disclaimer

Baseline is a valid AES-GCM + PBKDF2 construction used here only to quantify
**preprocessing overhead**. Do not interpret slower/faster as more/less secure.
