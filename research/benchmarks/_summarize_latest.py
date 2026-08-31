"""Print compact summary of latest benchmark JSON files."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "benchmarks" / "results"


def summarize(name: str) -> None:
    path = root / name
    if not path.is_file():
        print(f"missing {path}")
        return
    d = json.loads(path.read_text(encoding="utf-8"))
    env = d.get("environment", {})
    print("===", d.get("runtime"), "===")
    print(
        "os=",
        env.get("os"),
        "py=",
        env.get("python_version"),
        "node=",
        env.get("node_version"),
        "fw=",
        env.get("framework_version"),
        "crypto=",
        env.get("cryptography_version"),
        "cpus=",
        env.get("cpu_count"),
        "ram=",
        env.get("total_ram_bytes"),
    )
    for r in d.get("results", []):
        a = r["aryacrypt"]
        b = r["baseline"]
        kdf = a["t_kdf"]["mean"]
        staged = a["t_staged_enc_sum"]["mean"]
        pre = a["t_preprocess"]["mean"]
        share = 100 * kdf / staged if staged else None
        mem = r.get("memory") or {}
        print(
            f"{r['size_label']:6} n={r['runs']} "
            f"pre={pre:.6f} kdf={kdf:.4f} aes={a['t_aes_enc']['mean']:.6f} "
            f"e2eA={a['t_total_enc']['mean']:.4f} e2eB={b['t_total_enc']['mean']:.4f} "
            f"ohEnc={r.get('overhead_enc_pct_mean')} "
            f"ohDec={r.get('overhead_dec_pct_mean')} "
            f"pbkdf2%={share:.2f} "
            f"tp={a['throughput_aes_enc_mbs']['mean']:.1f} "
            f"preShare={a['preprocess_share']['mean']} "
            f"memPeak={mem.get('tracemalloc_peak_bytes')} "
            f"rssD={mem.get('rss_delta_bytes')} "
            f"heapD={mem.get('heap_delta_bytes')}"
        )


if __name__ == "__main__":
    summarize("python_latest.json")
    summarize("node_latest.json")
