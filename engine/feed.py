"""Loads bar data from parquet files and turns it into MarketEvents."""
from pathlib import Path

import pandas as pd

from .events import MarketEvent


def load_bars(data_dir, symbols, regular_hours_only=True):
    """Return one DataFrame of bars for all symbols, sorted by time."""
    frames = []
    for sym in symbols:
        df = pd.read_parquet(Path(data_dir) / f"{sym}_1min.parquet")
        df["symbol"] = sym
        frames.append(df[["symbol", "timestamp", "open", "high", "low", "close", "volume"]])
    bars = pd.concat(frames, ignore_index=True)
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)

    if regular_hours_only:
        # Keep 09:30 to 15:59 New York time; drop pre and post market bars
        ny = bars["timestamp"].dt.tz_convert("America/New_York")
        minutes = ny.dt.hour * 60 + ny.dt.minute
        bars = bars[(minutes >= 570) & (minutes < 960)]

    return bars.sort_values(["timestamp", "symbol"], kind="stable").reset_index(drop=True)


def to_events(bars):
    """Convert the bars DataFrame into a list of MarketEvents (built once, before timing)."""
    ts_ns = bars["timestamp"].dt.as_unit("ns").astype("int64").to_numpy()
    cols = [bars[c].to_numpy() for c in ("symbol", "open", "high", "low", "close", "volume")]
    return [
        MarketEvent(int(t), str(s), float(o), float(h), float(l), float(c), float(v))
        for t, s, o, h, l, c, v in zip(ts_ns, *cols)
    ]
