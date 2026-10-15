"""Print all benchmark results as a markdown table (paste into the README)."""
import json
from pathlib import Path

rows = sorted(Path("bench/results").glob("*.json"), key=lambda p: p.stat().st_mtime)
print("| Step | p50 (us) | p99 (us) | p99.9 (us) | Max (us) | Events/sec |")
print("| --- | --- | --- | --- | --- | --- |")
for path in rows:
    r = json.loads(path.read_text())
    print(f"| {r['label']} | {r['p50_us']:.2f} | {r['p99_us']:.2f} | {r['p999_us']:.2f} "
          f"| {r['max_us']:.1f} | {r['events_per_sec']:,.0f} |")
