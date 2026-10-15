"""Performance statistics from an equity curve."""
import numpy as np

NS_PER_YEAR = 365.25 * 24 * 3600 * 1e9


def summarize(equity_ts, equity):
    eq = np.asarray(equity, dtype=float)
    ts = np.asarray(equity_ts, dtype=np.int64)
    rets = np.diff(eq) / eq[:-1]

    years = (ts[-1] - ts[0]) / NS_PER_YEAR
    periods_per_year = len(rets) / years if years > 0 else 0.0
    std = rets.std(ddof=1) if len(rets) > 1 else 0.0
    sharpe = rets.mean() / std * np.sqrt(periods_per_year) if std > 0 else 0.0

    peak = np.maximum.accumulate(eq)
    return {
        "total_return_pct": (eq[-1] / eq[0] - 1) * 100,
        "sharpe": float(sharpe),
        "max_drawdown_pct": float((eq / peak - 1).min() * 100),
        "years": float(years),
    }
