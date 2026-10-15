"""Moving average crossover strategy with O(1) updates per bar."""
from collections import deque

from .events import SignalEvent


class MovingAverageCross:
    """Long when the fast average is above the slow average, flat otherwise."""

    def __init__(self, symbols, fast=20, slow=50):
        if fast >= slow:
            raise ValueError("fast window must be shorter than slow window")
        self.fast, self.slow = fast, slow
        self.fast_win = {s: deque() for s in symbols}
        self.slow_win = {s: deque() for s in symbols}
        self.fast_sum = {s: 0.0 for s in symbols}
        self.slow_sum = {s: 0.0 for s in symbols}
        self.state = {s: 0 for s in symbols}

    def on_market(self, ev):
        s, px = ev.symbol, ev.close

        fw = self.fast_win[s]
        fw.append(px)
        self.fast_sum[s] += px
        if len(fw) > self.fast:
            self.fast_sum[s] -= fw.popleft()

        sw = self.slow_win[s]
        sw.append(px)
        self.slow_sum[s] += px
        if len(sw) > self.slow:
            self.slow_sum[s] -= sw.popleft()

        if len(sw) < self.slow:
            return None  # not enough history yet

        direction = 1 if self.fast_sum[s] / self.fast > self.slow_sum[s] / self.slow else 0
        if direction != self.state[s]:
            self.state[s] = direction
            return SignalEvent(ev.ts, s, direction)
        return None
