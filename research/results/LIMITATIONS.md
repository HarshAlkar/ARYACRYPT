# Research and Benchmark Limitations

This note accompanies the AryaCrypt v1.1.0 performance study. It is intended for academic defence (viva) and responsible reporting.

## Scope of the measurements

1. **Machine dependence** — Absolute times (and to a lesser extent ratios) depend on CPU, power state, background load, OS, and library builds. Numbers from one laptop are not universal constants.

2. **Python vs Node** — The two runtimes use different crypto stacks and VMs. Wall-clock times must **not** be compared as if they were identical experimental conditions for “which language is faster at AryaCrypt.”

3. **Approximate memory metrics** — Python `tracemalloc` / RSS and Node `heapUsed` deltas are practical indicators, not formal memory-complexity proofs. Garbage collection and allocator behaviour introduce noise.

4. **PBKDF2 masks small costs** — With 600,000 PBKDF2-HMAC-SHA256 iterations, microsecond-scale RomanMapper work is easily lost in end-to-end variance. That is a measurement limitation for quantifying tiny absolute overheads via end-to-end timers alone (staged timers remain informative).

5. **Performance ≠ security** — Latency, throughput, and memory use do **not** prove cryptographic strength, resistance to attacks, or superiority over other designs.

6. **Aryabhata layer is not a new cipher** — RomanMapper / Aryabhata preprocessing is a **deterministic password-preprocessing / key-material transformation** feeding standard PBKDF2 and AES-256-GCM. It does not replace AES or invent a novel authenticated encryption scheme.

7. **No independent cryptanalysis in this work** — Formal security claims would require dedicated cryptanalysis beyond this engineering and performance study. None is claimed here.

8. **Reproducibility caveats** — Fixed salt/nonce are for **benchmark reproducibility**, not production guidance (production must use fresh CSPRNG salt/nonce per encryption).

9. **Workload model** — Benchmarks use in-memory buffers and a single password. Streaming I/O, disk, network, and concurrent multi-user loads are out of scope.

10. **Statistical power at 100 MiB** — Only three measured repeats were used for 100 MiB to keep wall time feasible; variance estimates there are coarser than for ≤1 MiB (ten repeats).
