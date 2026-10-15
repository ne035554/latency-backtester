"""Latency benchmark: time per market event, from arrival to order decision.

Usage:  python -m bench.bench --label baseline [--no-gc]
"""
import argparse
import gc
import json
import platform
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from engine.backtest import run
from engine.feed import load_bars, to_events

SYMBOLS = ["SPY", "QQQ", "AAPL", "MSFT"]
WARMUP = 10_000
RUNS = 5
RESULTS = Path("bench/results")


def read_file(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return ""


def cpu_model():
    for line in read_file("/proc/cpuinfo").splitlines():
        if line.startswith("model name"):
            return line.split(":", 1)[1].strip()
    return platform.processor()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="name for this run, e.g. baseline")
    ap.add_argument("--no-gc", action="store_true", help="freeze and disable the garbage collector")
    args = ap.parse_args()

    events = to_events(load_bars("data", SYMBOLS))
    gc.collect()
    if args.no_gc:
        gc.freeze()
        gc.disable()

    runs = []
    for r in range(RUNS):
        start = time.perf_counter()
        _, lat = run(events, SYMBOLS, record_latency=True)
        wall = time.perf_counter() - start
        us = lat[WARMUP:] / 1_000.0
        runs.append({
            "p50_us": float(np.percentile(us, 50)),
            "p99_us": float(np.percentile(us, 99)),
            "p999_us": float(np.percentile(us, 99.9)),
            "max_us": float(us.max()),
            "events_per_sec": len(events) / wall,
        })
        print(f"run {r + 1}/{RUNS}: p50={runs[-1]['p50_us']:.2f}us p99={runs[-1]['p99_us']:.2f}us "
              f"p99.9={runs[-1]['p999_us']:.2f}us max={runs[-1]['max_us']:.1f}us", flush=True)

    result = {k: float(np.median([run_[k] for run_ in runs])) for k in runs[0]}
    result.update({
        "label": args.label,
        "gc_disabled": args.no_gc,
        "events": len(events),
        "runs": RUNS,
        "cpu": cpu_model(),
        "kernel": platform.release(),
        "kernel_cmdline": read_file("/proc/cmdline"),
        "isolated_cpus": read_file("/sys/devices/system/cpu/isolated"),
        "python": platform.python_version(),
    })

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"{args.label}.json").write_text(json.dumps(result, indent=2))

    plt.figure(figsize=(8, 4))
    plt.hist(us, bins=np.logspace(np.log10(max(us.min(), 0.01)), np.log10(us.max()), 100))
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Latency per event (microseconds)")
    plt.ylabel("Events")
    plt.title(f"Tick to order latency: {args.label}")
    plt.tight_layout()
    plt.savefig(RESULTS / f"{args.label}.png", dpi=120)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
