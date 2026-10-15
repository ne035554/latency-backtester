"""Download 1 minute bars from Alpaca and save one parquet file per symbol."""
import os
from datetime import datetime
from pathlib import Path

from alpaca.data.enums import Adjustment, DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

SYMBOLS = ["SPY", "QQQ", "AAPL", "MSFT"]
START = datetime(2024, 1, 1)
END = datetime(2025, 12, 31)
OUT = Path("data")


def main():
    OUT.mkdir(exist_ok=True)
    client = StockHistoricalDataClient(os.environ["APCA_API_KEY_ID"], os.environ["APCA_API_SECRET_KEY"])
    for sym in SYMBOLS:
        path = OUT / f"{sym}_1min.parquet"
        if path.exists():
            print(f"{sym}: already downloaded, skipping")
            continue
        print(f"{sym}: downloading...", flush=True)
        req = StockBarsRequest(
            symbol_or_symbols=sym,
            timeframe=TimeFrame.Minute,
            start=START,
            end=END,
            adjustment=Adjustment.SPLIT,
            feed=DataFeed.SIP,
        )
        df = client.get_stock_bars(req).df.reset_index()
        df.to_parquet(path)
        print(f"{sym}: {len(df):,} bars saved to {path}")


if __name__ == "__main__":
    main()
