"""Paper-only minute-bar momentum prototypes for BTC-USD; no broker connections.
Coinbase Exchange candles are polled in historical batches. This is NOT live execution.
"""
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

END = dt.datetime(2026, 10, 22, 14, 56, tzinfo=dt.timezone.utc)
START = END - dt.timedelta(days=2)
FEE = .001
SLIPPAGE = .0005

def bars():
    out = {}
    cursor = int(START.timestamp())
    end = int(END.timestamp())
    while cursor < end:
        stop = min(cursor + 240 * 60, end)
        params = urllib.parse.urlencode({
            "start": dt.datetime.fromtimestamp(cursor, dt.timezone.utc).isoformat(),
            "end": dt.datetime.fromtimestamp(stop, dt.timezone.utc).isoformat(),
            "granularity": 60})
        req = urllib.request.Request("https://api.exchange.coinbase.com/products/BTC-USD/candles?" + params,
                                     headers={"User-Agent": "paper-momentum-research/1.0"})
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    candles = json.load(response)
                if not isinstance(candles, list):
                    raise RuntimeError("Unexpected response")
                for row in candles:
                    out[int(row[0])] = {"ts": int(row[0]), "close": float(row[4]),
                                        "volume": float(row[5])}
                break
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        cursor = stop
        time.sleep(.35)
    result = [out[t] for t in sorted(out)]
    if len(result) < 2500:
        raise RuntimeError("Insufficient minute bars")
    return result

def test(data, mode):
    cash, units, entry, peak, trades, wins, losses = 10000., 0., 0., 0., 0, 0, 0
    max_equity, drawdown = 10000., 0.
    holding = 0
    for i in range(31, len(data)):
        price = data[i]["close"]
        past = data[i-30:i]
        avg_volume = sum(b["volume"] for b in past) / len(past)
        vol_ratio = data[i]["volume"] / avg_volume if avg_volume else 0
        ret5 = price / data[i-5]["close"] - 1
        ret15 = price / data[i-15]["close"] - 1
        if units:
            holding += 1
            peak = max(peak, price)
            stop = .004 if mode == "scalper" else .015
            trail = .003 if mode == "scalper" else .012
            target = .008 if mode == "scalper" else .04
            limit = 12 if mode == "scalper" else 45
            if price <= entry * (1-stop) or price <= peak * (1-trail) or price >= entry * (1+target) or holding >= limit:
                proceeds = units * price * (1 - SLIPPAGE) * (1 - FEE)
                cash += proceeds
                wins += proceeds > (units * entry / (1+SLIPPAGE) / (1-FEE))
                losses += proceeds <= (units * entry / (1+SLIPPAGE) / (1-FEE))
                units, trades, holding = 0., trades+1, 0
        elif mode == "scalper" and ret5 > .002 and vol_ratio > 2 and ret15 > 0:
            spend = cash * .1
            units = spend * (1-FEE) / (price * (1+SLIPPAGE))
            cash -= spend
            entry, peak = price, price
        elif mode == "explosive" and ret5 > .008 and vol_ratio > 4 and ret15 > .012:
            spend = cash * .1
            units = spend * (1-FEE) / (price * (1+SLIPPAGE))
            cash -= spend
            entry, peak = price, price
        equity = cash + units * price * (1-SLIPPAGE) * (1-FEE)
        max_equity = max(max_equity, equity)
        drawdown = max(drawdown, (max_equity-equity)/max_equity)
    final = cash + units * data[-1]["close"] * (1-SLIPPAGE) * (1-FEE)
    return {"final_equity_usd": round(final, 2), "profit_usd": round(final-10000,2),
            "closed_trades": trades, "winning_trades": wins, "losing_trades": losses,
            "max_drawdown_pct": round(drawdown*100,3), "open_position": bool(units)}

if __name__ == "__main__":
    data = bars()
    report = {"market": "BTC-USD", "source": "Coinbase historical 1-minute bars",
              "period_start_utc": START.isoformat(), "period_end_utc": END.isoformat(),
              "bars": len(data), "assumed_fee_per_side": FEE,
              "assumed_slippage_per_side": SLIPPAGE,
              "warning": "Only two days of historical crypto data. Not validated for stocks or real execution; signals use candle close, so fills may be optimistic.",
              "scalper": test(data, "scalper"),
              "explosive": test(data, "explosive")}
    Path("minute_momentum_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
