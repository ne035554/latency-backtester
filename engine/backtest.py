"""The event loop: market event -> fill -> strategy -> signal -> order."""
import time

import numpy as np

from .execution import SimulatedExecution
from .portfolio import Portfolio
from .strategy import MovingAverageCross


def run(events, symbols, fast=20, slow=50, record_latency=False):
    strategy = MovingAverageCross(symbols, fast, slow)
    portfolio = Portfolio(symbols)
    execution = SimulatedExecution()

    latency = np.empty(len(events), dtype=np.int64) if record_latency else None
    clock = time.perf_counter_ns
    last_ts = None

    for i, ev in enumerate(events):
        # Snapshot equity once per timestamp (outside the timed section)
        if last_ts is not None and ev.ts != last_ts:
            portfolio.record_equity(last_ts)
        last_ts = ev.ts

        t0 = clock()
        # 1. Fill any order queued on the previous bar at this bar's open
        fill = execution.on_market(ev)
        if fill is not None:
            portfolio.on_fill(fill)
        # 2. Update prices, run the strategy, and route any new order
        portfolio.on_market(ev)
        signal = strategy.on_market(ev)
        if signal is not None:
            order = portfolio.on_signal(signal)
            if order is not None:
                execution.submit(order)
        if latency is not None:
            latency[i] = clock() - t0

    if last_ts is not None:
        portfolio.record_equity(last_ts)
    return portfolio, latency
