"""Event types that flow through the backtest loop."""
from dataclasses import dataclass


@dataclass(slots=True)
class MarketEvent:
    """One price bar for one symbol."""
    ts: int          # bar timestamp, nanoseconds since epoch (UTC)
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class SignalEvent:
    """Strategy decision: 1 = be long, 0 = be flat."""
    ts: int
    symbol: str
    direction: int


@dataclass(slots=True)
class OrderEvent:
    """Order to trade a number of shares (positive buy, negative sell)."""
    ts: int
    symbol: str
    quantity: int


@dataclass(slots=True)
class FillEvent:
    """Executed trade."""
    ts: int
    symbol: str
    quantity: int
    price: float
    commission: float
