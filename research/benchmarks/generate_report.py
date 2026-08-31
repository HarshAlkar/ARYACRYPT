#!/usr/bin/env python3
"""Aggregate benchmark JSON into CSV/JSON/Markdown + matplotlib graphs."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import PUBLISHED_RESULTS_DIR, RAW_RESULTS_DIR  # noqa: E402

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "matplotlib is required. Install: pip install -r research/benchmarks/requirements.txt"
    ) from exc


def load_latest(results_dir: Path, runtime: str) -> dict[str, Any] | None:
    latest = results_dir / f"{runtime}_latest.json"
    if latest.is_file():
        return json.loads(latest.read_text(encoding="utf-8"))
    candidates = sorted(results_dir.glob(f"{runtime}_*.json"), reverse=True)
    candidates = [p for p in candidates if p.name != f"{runtime}_latest.json"]
    if not candidates:
        return None
    return json.loads(candidates[0].read_text(encoding="utf-8"))


def flatten_rows(doc: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    runtime = doc.get("runtime", "unknown")
    env = doc.get("environment", {})
    for item in doc.get("results", []):
        size = item["size_bytes"]
        label = item["size_label"]
        for path_name in ("aryacrypt", "baseline"):
            stats = item.get(path_name, {})
            row = {
                "runtime": runtime,
                "path": path_name,
                "size_bytes": size,
                "size_label": label,
                "runs": item.get("runs"),
                "overhead_enc_pct_mean": item.get("overhead_enc_pct_mean")
                if path_name == "aryacrypt"
                else None,
                "overhead_dec_pct_mean": item.get("overhead_dec_pct_mean")
                if path_name == "aryacrypt"
                else None,
                "python_version": env.get("python_version"),
                "node_version": env.get("node_version"),
                "framework_version": env.get("framework_version")
                or doc.get("config", {}).get("framework_version"),
                "os": env.get("os"),
            }
            for metric, agg in stats.items():
                if isinstance(agg, dict) and "mean" in agg:
                    row[f"{metric}_mean"] = agg.get("mean")
                    row[f"{metric}_median"] = agg.get("median")
                    row[f"{metric}_min"] = agg.get("min")
                    row[f"{metric}_max"] = agg.get("max")
                    row[f"{metric}_stdev"] = agg.get("stdev")
            rows.append(row)
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    seen = set()
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def write_markdown(
    docs: list[dict[str, Any]], rows: list[dict[str, Any]], path: Path
) -> None:
    lines = [
        "# AryaCrypt Benchmark Report",
        "",
        "> **Disclaimer:** These are **performance** measurements only. "
        "They are **not** evidence of cryptographic strength. "
        "The baseline (UTF-8 password → PBKDF2 → AES-256-GCM) is a valid construction "
        "used solely to quantify Aryabhata/RomanMapper preprocessing overhead.",
        "",
    ]
    for doc in docs:
        env = doc.get("environment", {})
        lines.append(f"## Environment ({doc.get('runtime')})")
        lines.append("")
        lines.append(f"- OS: `{env.get('os')} {env.get('os_release', '')}`".rstrip())
        lines.append(f"- Machine: `{env.get('machine')}`")
        if env.get("cpu_count"):
            lines.append(f"- CPU count: `{env.get('cpu_count')}`")
        if env.get("processor"):
            lines.append(f"- Processor: `{env.get('processor')}`")
        if env.get("cpu_model"):
            lines.append(f"- CPU model: `{env.get('cpu_model')}`")
        if env.get("python_version"):
            lines.append(f"- Python: `{env.get('python_version')}`")
        if env.get("node_version"):
            lines.append(f"- Node: `{env.get('node_version')}`")
        lines.append(f"- Framework: `{env.get('framework_version')}`")
        lines.append(f"- Package: `{env.get('package_version')}`")
        if env.get("cryptography_version"):
            lines.append(f"- cryptography: `{env.get('cryptography_version')}`")
        if env.get("total_ram_bytes"):
            gb = env["total_ram_bytes"] / (1024**3)
            lines.append(f"- RAM: `{gb:.1f} GiB`")
        lines.append(f"- Timestamp (UTC): `{env.get('timestamp_utc')}`")
        lines.append("")

    lines.extend(
        [
            "## Summary table (mean end-to-end times)",
            "",
            "| Runtime | Path | Size | Enc mean (s) | Dec mean (s) | AES enc MB/s | Overhead enc % |",
            "|---------|------|------|--------------|--------------|--------------|----------------|",
        ]
    )
    for r in rows:
        lines.append(
            "| {runtime} | {path} | {size_label} | {enc} | {dec} | {aes} | {oh} |".format(
                runtime=r.get("runtime"),
                path=r.get("path"),
                size_label=r.get("size_label"),
                enc=_fmt(r.get("t_total_enc_mean")),
                dec=_fmt(r.get("t_total_dec_mean")),
                aes=_fmt(r.get("throughput_aes_enc_mbs_mean")),
                oh=_fmt(r.get("overhead_enc_pct_mean")),
            )
        )
    lines.extend(
        [
            "",
            "## Graphs",
            "",
            "Generated from measured JSON (see PNG files in this directory):",
            "",
            "- `graph_enc_time.png` — file size vs encryption time",
            "- `graph_dec_time.png` — file size vs decryption time",
            "- `graph_throughput.png` — file size vs AES encrypt throughput",
            "- `graph_preprocess_overhead.png` — preprocessing time / overhead %",
            "- `graph_total_comparison.png` — baseline vs AryaCrypt total encrypt time",
            "- `graph_pbkdf2_share.png` — PBKDF2 share of staged encryption runtime",
            "- `graph_memory.png` — memory usage vs file size",
            "",
            "## Methodology",
            "",
            "1. Fixed password, salt, and nonce from Spec vector `basic-ascii`.",
            "2. Deterministic plaintext fill (seeded PRNG).",
            "3. Multiple timed iterations; report mean/median/min/max/stdev.",
            "4. AryaCrypt path uses RomanMapper stream as PBKDF2 password material.",
            "5. Baseline uses UTF-8(password) as PBKDF2 password material.",
            "",
            "See also `PERFORMANCE_ANALYSIS.md`, `LIMITATIONS.md`, and `RESEARCH_SUMMARY.md`.",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt(v: Any) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.6g}"
    return str(v)


def plot_graphs(docs: list[dict[str, Any]], out_dir: Path) -> None:
    # Prefer python doc for primary graphs; overlay node if present
    for doc in docs:
        runtime = doc.get("runtime", "unknown")
        sizes = []
        labels = []
        arya_enc = []
        base_enc = []
        arya_dec = []
        base_dec = []
        arya_tp = []
        base_tp = []
        pre_t = []
        overhead = []
        pbkdf2_share_enc = []
        mem_peak = []
        mem_rss_delta = []
        mem_heap_delta = []

        for item in doc.get("results", []):
            sizes.append(item["size_bytes"])
            labels.append(item["size_label"])
            arya = item["aryacrypt"]
            base = item["baseline"]
            arya_enc.append(arya["t_total_enc"]["mean"])
            base_enc.append(base["t_total_enc"]["mean"])
            arya_dec.append(arya["t_total_dec"]["mean"])
            base_dec.append(base["t_total_dec"]["mean"])
            arya_tp.append(arya["throughput_aes_enc_mbs"]["mean"])
            base_tp.append(base["throughput_aes_enc_mbs"]["mean"])
            pre_t.append(arya["t_preprocess"]["mean"])
            overhead.append(item.get("overhead_enc_pct_mean"))

            # PBKDF2 share of staged encrypt sum (preprocess + kdf + aes_enc)
            kdf_m = arya.get("t_kdf", {}).get("mean")
            staged_m = arya.get("t_staged_enc_sum", {}).get("mean")
            if kdf_m is not None and staged_m and staged_m > 0:
                pbkdf2_share_enc.append(100.0 * kdf_m / staged_m)
            else:
                pbkdf2_share_enc.append(None)

            mem = item.get("memory") or {}
            mem_peak.append(mem.get("tracemalloc_peak_bytes"))
            mem_rss_delta.append(mem.get("rss_delta_bytes"))
            mem_heap_delta.append(mem.get("heap_delta_bytes"))

        x = list(range(len(labels)))

        def _save(name: str):
            plt.tight_layout()
            plt.savefig(out_dir / name, dpi=150)
            plt.close()

        # Academic-ish style defaults
        plt.rcParams.update(
            {
                "font.size": 10,
                "axes.titlesize": 11,
                "axes.labelsize": 10,
                "figure.facecolor": "white",
                "axes.facecolor": "white",
            }
        )

        # 1 Encryption time
        plt.figure(figsize=(8, 5))
        plt.plot(x, base_enc, "o-", label="Baseline E2E enc")
        plt.plot(x, arya_enc, "s-", label="AryaCrypt E2E enc")
        plt.xticks(x, labels)
        plt.xlabel("File size")
        plt.ylabel("Mean time (s)")
        plt.title(f"File size vs encryption time ({runtime})")
        plt.legend()
        plt.grid(True, alpha=0.3)
        _save(f"graph_enc_time_{runtime}.png")

        # 2 Decryption time
        plt.figure(figsize=(8, 5))
        plt.plot(x, base_dec, "o-", label="Baseline E2E dec")
        plt.plot(x, arya_dec, "s-", label="AryaCrypt E2E dec")
        plt.xticks(x, labels)
        plt.xlabel("File size")
        plt.ylabel("Mean time (s)")
        plt.title(f"File size vs decryption time ({runtime})")
        plt.legend()
        plt.grid(True, alpha=0.3)
        _save(f"graph_dec_time_{runtime}.png")

        # 3 Throughput
        plt.figure(figsize=(8, 5))
        plt.plot(x, base_tp, "o-", label="Baseline AES enc")
        plt.plot(x, arya_tp, "s-", label="AryaCrypt AES enc")
        plt.xticks(x, labels)
        plt.xlabel("File size")
        plt.ylabel("Mean throughput (MB/s)")
        plt.title(f"File size vs AES encrypt throughput ({runtime})")
        plt.legend()
        plt.grid(True, alpha=0.3)
        _save(f"graph_throughput_{runtime}.png")

        # 4 Preprocess + overhead %
        fig, ax1 = plt.subplots(figsize=(8, 5))
        ax1.plot(x, pre_t, "s-", color="C0", label="Preprocess time")
        ax1.set_xlabel("File size")
        ax1.set_ylabel("Mean preprocess time (s)", color="C0")
        ax2 = ax1.twinx()
        ax2.plot(x, overhead, "^-", color="C1", label="E2E enc overhead %")
        ax2.set_ylabel("Overhead vs baseline (%)", color="C1")
        ax1.set_xticks(x)
        ax1.set_xticklabels(labels)
        ax1.set_title(f"AryaCrypt preprocessing overhead ({runtime})")
        ax1.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(out_dir / f"graph_preprocess_overhead_{runtime}.png", dpi=150)
        plt.close(fig)

        # 5 Total comparison bar
        plt.figure(figsize=(9, 5))
        width = 0.35
        xs = list(range(len(labels)))
        plt.bar([i - width / 2 for i in xs], base_enc, width, label="Baseline")
        plt.bar([i + width / 2 for i in xs], arya_enc, width, label="AryaCrypt")
        plt.xticks(xs, labels)
        plt.ylabel("Mean E2E encrypt time (s)")
        plt.title(f"Baseline vs AryaCrypt total encrypt time ({runtime})")
        plt.legend()
        plt.grid(True, axis="y", alpha=0.3)
        _save(f"graph_total_comparison_{runtime}.png")

        # 6 PBKDF2 share of staged encrypt runtime
        plt.figure(figsize=(8, 5))
        valid_x = [i for i, v in enumerate(pbkdf2_share_enc) if v is not None]
        valid_y = [pbkdf2_share_enc[i] for i in valid_x]
        plt.plot(valid_x, valid_y, "D-", color="C3", label="PBKDF2 share of staged enc")
        plt.xticks(x, labels)
        plt.xlabel("File size")
        plt.ylabel("PBKDF2 share (%)")
        plt.ylim(0, 105)
        plt.title(f"PBKDF2 share of staged encryption runtime ({runtime})")
        plt.legend()
        plt.grid(True, alpha=0.3)
        _save(f"graph_pbkdf2_share_{runtime}.png")

        # 7 Memory vs file size
        plt.figure(figsize=(8, 5))
        plotted = False
        if any(v is not None for v in mem_peak):
            ys = [(v / (1024 * 1024)) if v is not None else None for v in mem_peak]
            plt.plot(x, ys, "o-", label="tracemalloc peak (MiB)")
            plotted = True
        if any(v is not None for v in mem_rss_delta):
            ys = [(v / (1024 * 1024)) if v is not None else None for v in mem_rss_delta]
            plt.plot(x, ys, "s-", label="RSS delta (MiB)")
            plotted = True
        if any(v is not None for v in mem_heap_delta):
            ys = [(v / (1024 * 1024)) if v is not None else None for v in mem_heap_delta]
            plt.plot(x, ys, "^-", label="heap delta (MiB)")
            plotted = True
        if not plotted:
            plt.text(0.5, 0.5, "No memory samples", ha="center", transform=plt.gca().transAxes)
        plt.xticks(x, labels)
        plt.xlabel("File size")
        plt.ylabel("Memory (MiB)")
        plt.title(f"Memory usage vs file size ({runtime})")
        plt.legend()
        plt.grid(True, alpha=0.3)
        _save(f"graph_memory_{runtime}.png")

    # Canonical names expected by README (prefer python)
    preferred = next((d for d in docs if d.get("runtime") == "python"), docs[0])
    rt = preferred.get("runtime")
    for src_suffix, dest in [
        (f"graph_enc_time_{rt}.png", "graph_enc_time.png"),
        (f"graph_dec_time_{rt}.png", "graph_dec_time.png"),
        (f"graph_throughput_{rt}.png", "graph_throughput.png"),
        (f"graph_preprocess_overhead_{rt}.png", "graph_preprocess_overhead.png"),
        (f"graph_total_comparison_{rt}.png", "graph_total_comparison.png"),
        (f"graph_pbkdf2_share_{rt}.png", "graph_pbkdf2_share.png"),
        (f"graph_memory_{rt}.png", "graph_memory.png"),
    ]:
        src = out_dir / src_suffix
        if src.is_file():
            dest_path = out_dir / dest
            dest_path.write_bytes(src.read_bytes())


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Generate AryaCrypt benchmark report")
    p.add_argument("--results-dir", type=Path, default=RAW_RESULTS_DIR)
    p.add_argument("--out-dir", type=Path, default=PUBLISHED_RESULTS_DIR)
    p.add_argument("--input", type=Path, nargs="*", help="Explicit JSON files")
    args = p.parse_args(argv)

    docs: list[dict[str, Any]] = []
    if args.input:
        for path in args.input:
            docs.append(json.loads(path.read_text(encoding="utf-8")))
    else:
        for runtime in ("python", "node"):
            doc = load_latest(args.results_dir, runtime)
            if doc:
                docs.append(doc)

    if not docs:
        raise SystemExit(
            f"No benchmark JSON found in {args.results_dir}. "
            "Run benchmark_python.py or benchmark_node.ts first."
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for doc in docs:
        rows.extend(flatten_rows(doc))

    report_json = {
        "disclaimer": docs[0].get("disclaimer"),
        "documents": [
            {
                "runtime": d.get("runtime"),
                "environment": d.get("environment"),
                "config": d.get("config"),
                "results": [
                    {
                        "size_bytes": r["size_bytes"],
                        "size_label": r["size_label"],
                        "runs": r["runs"],
                        "overhead_enc_pct_mean": r.get("overhead_enc_pct_mean"),
                        "overhead_dec_pct_mean": r.get("overhead_dec_pct_mean"),
                        "aryacrypt": {
                            k: r["aryacrypt"][k]
                            for k in r["aryacrypt"]
                            if k
                            in (
                                "t_preprocess",
                                "t_kdf",
                                "t_aes_enc",
                                "t_aes_dec",
                                "t_total_enc",
                                "t_total_dec",
                                "throughput_aes_enc_mbs",
                                "throughput_e2e_enc_mbs",
                            )
                        },
                        "baseline": {
                            k: r["baseline"][k]
                            for k in r["baseline"]
                            if k
                            in (
                                "t_kdf",
                                "t_aes_enc",
                                "t_aes_dec",
                                "t_total_enc",
                                "t_total_dec",
                                "throughput_aes_enc_mbs",
                                "throughput_e2e_enc_mbs",
                            )
                        },
                        "memory": r.get("memory"),
                    }
                    for r in d.get("results", [])
                ],
            }
            for d in docs
        ],
        "flat_rows": rows,
    }

    (args.out_dir / "benchmark_report.json").write_text(
        json.dumps(report_json, indent=2), encoding="utf-8"
    )
    write_csv(rows, args.out_dir / "benchmark_report.csv")
    write_markdown(docs, rows, args.out_dir / "benchmark_report.md")
    plot_graphs(docs, args.out_dir)

    print(f"Wrote report artifacts to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
