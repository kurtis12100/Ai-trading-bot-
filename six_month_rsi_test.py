"""Six-month BTC-USD historical replay of the preselected RSI strategy. Paper only."""
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from strategy_trials import simulate

END = dt.datetime(2026, 10, 22, 14, 56, tzinfo=dt.timezone.utc)
START = dt.datetime(2026, 4, 22, 14, 56, tzinfo=dt.timezone.utc)
CONFIG = ("rsi", 12, 30, 0.001, 0.20)
GRANULARITY = 3600

def get_candles():
    # Coinbase Exchange public historical candles endpoint: max 300 per request.
    # Retrieve overlapping windows, deduplicate by UTC timestamp, and check coverage.
    begin = int(START.timestamp()) - 48 * GRANULARITY
    end = int(END.timestamp())
    rows = {}
    cursor = begin
    while cursor < end:
        stop = min(cursor + 250 * GRANULARITY, end)
        params = urllib.parse.urlencode({
            "start": dt.datetime.fromtimestamp(cursor, dt.timezone.utc).isoformat(),
            "end": dt.datetime.fromtimestamp(stop, dt.timezone.utc).isoformat(),
            "granularity": GRANULARITY,
        })
        url = "https://api.exchange.coinbase.com/products/BTC-USD/candles?" + params
        req = urllib.request.Request(url, headers={"User-Agent": "paper-bot-six-month-backtest/1.0"})
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = json.load(response)
                if not isinstance(data, list):
                    raise RuntimeError("Unexpected Coinbase response: " + str(data)[:250])
                for candle in data:
                    rows[int(candle[0])] = float(candle[4])  # Coinbase [time,low,high,open,close,volume]
                break
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        cursor = stop
        time.sleep(0.4)
    result = sorted(rows.items())
    if not result:
        raise RuntimeError("No historical candles returned")
    target = [t for t, _ in result if int(START.timestamp()) <= t < end]
    expected = (end - int(START.timestamp())) // GRANULARITY
    if len(target) < expected * 0.97:
        raise RuntimeError(f"Incomplete history: {len(target)} of about {expected} hourly candles")
    return result, len(target), expected

if __name__ == "__main__":
    rows, observed, expected = get_candles()
    result = simulate(rows, CONFIG, int(START.timestamp()), int(END.timestamp()))
    first = next(p for t, p in rows if t >= int(START.timestamp()))
    last = next(p for t, p in reversed(rows) if t < int(END.timestamp()))
    report = {
        "market": "BTC-USD",
        "source": "Coinbase Exchange public hourly historical candles",
        "start_utc": START.isoformat(),
        "end_utc": END.isoformat(),
        "strategy": {"family": "rsi", "lookback_hours": 12, "threshold": 0.001, "allocation": 0.20},
        "starting_cash_usd": 10000,
        "fee_per_trade": 0.001,
        "slippage_or_spread_included": False,
        "observed_hourly_candles": observed,
        "expected_hourly_candles_approx": expected,
        "strategy_result": result,
        "btc_buy_and_hold_return_pct": round((last / first - 1) * 100, 3),
        "caveat": "Historical backtest, not a forward result. Coinbase data differs from earlier Kraken test. No slippage/spread modeled. Paper only."
    }
    Path("six_month_rsi_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
