"""Simulated broker: fills orders at the next bar's open with slippage and commission."""
from .events import FillEvent


class SimulatedExecution:
    def __init__(self, slippage_bps=1.0, commission_per_share=0.005):
        self.slippage = slippage_bps / 10_000
        self.commission_per_share = commission_per_share
        self.pending = {}   # symbol -> OrderEvent waiting for the next bar

    def submit(self, order):
        self.pending[order.symbol] = order

    def on_market(self, ev):
        order = self.pending.pop(ev.symbol, None)
        if order is None:
            return None
        if order.quantity > 0:
            price = ev.open * (1 + self.slippage)   # buys pay up
        else:
            price = ev.open * (1 - self.slippage)   # sells give up
        commission = abs(order.quantity) * self.commission_per_share
        return FillEvent(ev.ts, ev.symbol, order.quantity, price, commission)
