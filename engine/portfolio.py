"""Tracks cash, positions and equity; turns signals into orders."""
from .events import OrderEvent


class Portfolio:
    def __init__(self, symbols, initial_cash=100_000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.alloc = initial_cash / len(symbols)   # fixed dollar budget per symbol
        self.positions = {s: 0 for s in symbols}
        self.last_price = {s: 0.0 for s in symbols}
        self.fills = []                            # trade log
        self.equity_ts = []
        self.equity = []

    def on_market(self, ev):
        self.last_price[ev.symbol] = ev.close

    def on_signal(self, sig):
        pos = self.positions[sig.symbol]
        if sig.direction == 1 and pos == 0:
            qty = int(self.alloc // self.last_price[sig.symbol])
            return OrderEvent(sig.ts, sig.symbol, qty) if qty > 0 else None
        if sig.direction == 0 and pos > 0:
            return OrderEvent(sig.ts, sig.symbol, -pos)
        return None

    def on_fill(self, fill):
        self.cash -= fill.quantity * fill.price + fill.commission
        self.positions[fill.symbol] += fill.quantity
        self.fills.append(fill)

    def record_equity(self, ts):
        value = self.cash
        for sym, qty in self.positions.items():
            if qty:
                value += qty * self.last_price[sym]
        self.equity_ts.append(ts)
        self.equity.append(value)
