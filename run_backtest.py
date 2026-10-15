"""Run the crossover backtest on the downloaded data and print the results."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from engine.backtest import run
from engine.feed import load_bars, to_events
from engine.metrics import summarize

SYMBOLS = ["SPY", "QQQ", "AAPL", "MSFT"]


def main():
    bars = load_bars("data", SYMBOLS)
    events = to_events(bars)
    print(f"Loaded {len(events):,} market events")

    portfolio, _ = run(events, SYMBOLS)
    stats = summarize(portfolio.equity_ts, portfolio.equity)

    print(f"Trades:        {len(portfolio.fills):,}")
    print(f"Total return:  {stats['total_return_pct']:.2f}%")
    print(f"Sharpe ratio:  {stats['sharpe']:.2f}")
    print(f"Max drawdown:  {stats['max_drawdown_pct']:.2f}%")
    print(f"Period:        {stats['years']:.2f} years")

    curve = pd.Series(portfolio.equity, index=pd.to_datetime(portfolio.equity_ts, utc=True))
    ax = curve.plot(figsize=(10, 4), title="Equity curve: 20/50 moving average crossover")
    ax.set_ylabel("Equity ($)")
    plt.tight_layout()
    plt.savefig("bench/results/equity_curve.png", dpi=120)
    print("Saved bench/results/equity_curve.png")


if __name__ == "__main__":
    main()
