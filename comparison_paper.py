"""Independent, paper-only hourly BTC strategy comparison. No trading credentials."""
import json, urllib.request
from datetime import datetime, timezone
from pathlib import Path

STATE = Path("comparison_state.json")
FEE = 0.001
SLIPPAGE = 0.0005
ALLOCATION = 0.10
START = 10000.0
NAMES = ("sma", "bollinger", "rsi_trend")

def candles():
    url = "https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=60"
    with urllib.request.urlopen(url, timeout=25) as response:
        payload = json.load(response)
    if payload.get("error"):
        raise RuntimeError(str(payload["error"]))
    key = next(k for k in payload["result"] if k != "last")
    # Last candle is unfinished; never trade on it.
    return [(int(row[0]), float(row[4])) for row in payload["result"][key][:-1]]

def rsi(values, n=14):
    changes = [values[i] - values[i-1] for i in range(len(values)-n, len(values))]
    gain = sum(max(x, 0) for x in changes) / n
    loss = sum(max(-x, 0) for x in changes) / n
    return 100 if loss == 0 else 100 - 100 / (1 + gain/loss)

def signal(name, closes):
    if len(closes) < 51:
        return "HOLD"
    if name == "sma":
        short = sum(closes[-10:])/10
        long = sum(closes[-30:])/30
        return "BUY" if short > long else "SELL"
    if name == "bollinger":
        subset = closes[-18:]
        avg = sum(subset)/18
        sd = (sum((x-avg)**2 for x in subset)/18)**0.5
        # Mean-reversion entry on 2 std-dev lower band, exit at mean.
        return "BUY" if closes[-1] < avg-2*sd else "SELL" if closes[-1] >= avg else "HOLD"
    strength = rsi(closes)
    trend = sum(closes[-50:])/50
    return "BUY" if strength < 35 and closes[-1] > trend else "SELL" if strength > 60 or closes[-1] < trend else "HOLD"

def main():
    rows = candles()
    if len(rows) < 52:
        raise RuntimeError("Not enough completed candles")
    now = datetime.now(timezone.utc).isoformat()
    state = json.loads(STATE.read_text()) if STATE.exists() else {
        "started_utc": now,
        "strategies": {n: {"cash": START, "btc": 0, "entry": None,
                            "day": "", "day_start_equity": START,
                            "trades": [], "equity_history": []} for n in NAMES}
    }
    last = state.get("last_candle", 0)
    if rows[-1][0] <= last:
        print("No new completed candle")
        return
    # Replay only candles after last checkpoint; avoid using future observations.
    for i, (ts, price) in enumerate(rows):
        if ts <= last or i < 51:
            continue
        day = datetime.fromtimestamp(ts, timezone.utc).date().isoformat()
        for name, s in state["strategies"].items():
            equity = s["cash"] + s["btc"] * price
            if s["day"] != day:
                s["day"], s["day_start_equity"] = day, equity
            action = signal(name, [p for _, p in rows[:i+1]])
            if s["btc"] and s["entry"] and price <= s["entry"] * 0.97:
                action = "SELL"  # 3% stop; hourly candle close, not guaranteed fill.
            if equity <= s["day_start_equity"] * 0.98:
                action = "SELL" if s["btc"] else "HOLD"  # 2% daily loss circuit breaker.
            if action == "BUY" and not s["btc"] and equity > s["day_start_equity"] * 0.98:
                spend = s["cash"] * ALLOCATION
                execution = price * (1 + SLIPPAGE)
                s["btc"] = spend * (1-FEE) / execution
                s["cash"] -= spend
                s["entry"] = execution
                s["trades"].append({"utc": ts, "side": "BUY", "price": execution})
            elif action == "SELL" and s["btc"]:
                execution = price * (1-SLIPPAGE)
                s["cash"] += s["btc"] * execution * (1-FEE)
                s["btc"], s["entry"] = 0, None
                s["trades"].append({"utc": ts, "side": "SELL", "price": execution})
            s["equity_history"].append({"utc": ts, "equity": round(s["cash"]+s["btc"]*price, 2)})
        state["last_candle"] = ts
    state["updated_utc"] = now
    state["assumptions"] = "USD; 0.1% fee and 0.05% slippage per side; 10% allocation; 3% close-based stop; 2% UTC-day circuit breaker; simulated hourly-close fills. No real orders."
    STATE.write_text(json.dumps(state, indent=2))
    for name, s in state["strategies"].items():
        print(name, "equity", s["equity_history"][-1]["equity"], "actions", len(s["trades"]))

if __name__ == "__main__":
    main()
