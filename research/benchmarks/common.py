"""Shared constants and helpers for AryaCrypt research benchmarks."""

from __future__ import annotations

import platform
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

# Spec-aligned fixed inputs (from docs/spec/test-vectors basic-ascii)
PASSWORD = "password1"
SALT = bytes.fromhex("00112233445566778899aabbccddeeff")
NONCE = bytes.fromhex("0102030405060708090a0b0c")
PLAINTEXT_SEED = 42

# Sizes in bytes: 1 KiB, 100 KiB, 1 MiB, 10 MiB, 100 MiB
SIZE_LABELS = {
    1024: "1KB",
    100 * 1024: "100KB",
    1024 * 1024: "1MB",
    10 * 1024 * 1024: "10MB",
    100 * 1024 * 1024: "100MB",
}

DEFAULT_SIZES = tuple(SIZE_LABELS.keys())
QUICK_SIZES = (1024, 100 * 1024, 1024 * 1024)  # omit 10MB / 100MB

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS_DIR = Path(__file__).resolve().parent
RAW_RESULTS_DIR = BENCHMARKS_DIR / "results"
PUBLISHED_RESULTS_DIR = REPO_ROOT / "research" / "results"


def size_label(n: int) -> str:
    return SIZE_LABELS.get(n, f"{n}B")


def default_runs_for_size(size: int) -> int:
    if size <= 1024 * 1024:
        return 10
    if size <= 10 * 1024 * 1024:
        return 5
    return 3


def should_warmup(size: int) -> bool:
    return size < 100 * 1024 * 1024


def make_plaintext(size: int, seed: int = PLAINTEXT_SEED) -> bytes:
    """Deterministic pseudo-random bytes (reproducible across runs)."""
    # xorshift-ish expansion from seed — no crypto RNG needed for payload fill
    out = bytearray(size)
    state = seed & 0xFFFFFFFF
    for i in range(size):
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= (state >> 17) & 0xFFFFFFFF
        state ^= (state << 5) & 0xFFFFFFFF
        out[i] = state & 0xFF
    return bytes(out)


def summarize(samples: Sequence[float]) -> dict[str, float | None]:
    if not samples:
        return {
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "stdev": None,
            "n": 0,
        }
    n = len(samples)
    return {
        "mean": float(statistics.mean(samples)),
        "median": float(statistics.median(samples)),
        "min": float(min(samples)),
        "max": float(max(samples)),
        "stdev": float(statistics.stdev(samples)) if n > 1 else 0.0,
        "n": n,
    }


def throughput_mbs(size_bytes: int, seconds: float | None) -> float | None:
    if seconds is None or seconds <= 0:
        return None
    return (size_bytes / 1_000_000.0) / seconds


def overhead_pct(arya: float | None, baseline: float | None) -> float | None:
    if arya is None or baseline is None or baseline <= 0:
        return None
    return ((arya - baseline) / baseline) * 100.0


def collect_env_python() -> dict[str, Any]:
    env: dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": "python",
        "os": platform.system(),
        "os_release": platform.release(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or None,
        "cpu_count": None,
        "python_version": sys.version.split()[0],
        "framework_version": None,
        "package_version": None,
        "cryptography_version": None,
        "total_ram_bytes": None,
        "psutil_available": False,
    }
    try:
        import os

        env["cpu_count"] = os.cpu_count()
    except Exception:
        pass

    try:
        import aryacrypt
        from aryacrypt import FRAMEWORK_VERSION

        env["package_version"] = getattr(aryacrypt, "__version__", None)
        env["framework_version"] = FRAMEWORK_VERSION
    except Exception as exc:
        env["aryacrypt_import_error"] = str(exc)

    try:
        import cryptography

        env["cryptography_version"] = cryptography.__version__
    except Exception:
        pass

    try:
        import psutil

        env["psutil_available"] = True
        env["total_ram_bytes"] = int(psutil.virtual_memory().total)
    except Exception:
        pass

    return env


def aggregate_metric_lists(runs: Iterable[dict[str, float | None]], keys: Sequence[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in keys:
        vals = [r[key] for r in runs if r.get(key) is not None]
        stats = summarize([float(v) for v in vals])  # type: ignore[arg-type]
        out[key] = stats
    return out
