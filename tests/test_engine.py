import numpy as np
import pandas as pd

from engine.backtest import run
from engine.events import MarketEvent
from engine.execution import SimulatedExecution
from engine.metrics import summarize


def make_events(closes, symbol="TEST", start_ns=0, step_ns=60_000_000_000):
    events = []
    prev = closes[0]
    for i, c in enumerate(closes):
        events.append(MarketEvent(start_ns + i * step_ns, symbol, prev, max(prev, c), min(prev, c), c, 1000.0))
        prev = c
    return events


def test_fill_happens_on_next_bar_open():
    """No look ahead: a signal on bar t fills at the OPEN of bar t+1."""
    closes = [100.0] * 50 + [110.0, 111.0, 112.0]   # jump on bar 50 turns the fast average above the slow one
    events = make_events(closes)
    portfolio, _ = run(events, ["TEST"], fast=2, slow=50)
    first = portfolio.fills[0]
    assert first.quantity > 0
    assert first.ts == events[51].ts                         # bar after the signal bar
    assert np.isclose(first.price, events[51].open * 1.0001)  # next open plus 1 bp slippage


def test_cash_accounting_round_trip():
    ex = SimulatedExecution(slippage_bps=0, commission_per_share=0.01)
    from engine.events import OrderEvent
    from engine.portfolio import Portfolio
    p = Portfolio(["TEST"], initial_cash=10_000)
    ex.submit(OrderEvent(0, "TEST", 10))
    p.on_fill(ex.on_market(MarketEvent(1, "TEST", 100, 100, 100, 100, 1)))
    ex.submit(OrderEvent(1, "TEST", -10))
    p.on_fill(ex.on_market(MarketEvent(2, "TEST", 105, 105, 105, 105, 1)))
    # bought 10 at 100, sold 10 at 105, paid 0.10 commission each way
    assert p.positions["TEST"] == 0
    assert np.isclose(p.cash, 10_000 + 10 * 5 - 0.20)


def test_trades_match_vectorized_pandas():
    """The event engine must trade on exactly the bars a vectorized pandas version predicts."""
    rng = np.random.default_rng(7)
    closes = list(100 * np.exp(np.cumsum(rng.normal(0, 0.002, 5_000))))
    events = make_events(closes)
    portfolio, _ = run(events, ["TEST"], fast=20, slow=50)

    s = pd.Series(closes)
    long = (s.rolling(20).mean() > s.rolling(50).mean()).astype(int)
    long[:49] = 0
    changes = long.diff().fillna(long.iloc[0])
    expected = [(i + 1, int(np.sign(c))) for i, c in changes.items() if c != 0 and i + 1 < len(events)]

    actual = [(int(f.ts // 60_000_000_000), int(np.sign(f.quantity))) for f in portfolio.fills]
    assert actual == expected


def test_metrics_on_known_curve():
    day = 24 * 3600 * 10**9
    stats = summarize([0, day, 2 * day], [100.0, 110.0, 99.0])
    assert np.isclose(stats["total_return_pct"], -1.0)
    assert np.isclose(stats["max_drawdown_pct"], -10.0)
