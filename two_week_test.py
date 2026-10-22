"""14-day BTC/USD historical replay and forward paper test. No live orders."""
import argparse
import csv
import datetime as dt
import json
import urllib.request
from pathlib import Path

START = dt.datetime(2026, 10, 22, 14, 56, tzinfo=dt.timezone.utc)
END = START + dt.timedelta(days=14)
FEE = 0.001
CASH = 10000.0
STATE = Path("forward_state.json")
REPORT = Path("backtest_report.json")

def candles():
    with urllib.request.urlopen("https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=60", timeout=30) as r:
        data = json.load(r)
    if data.get("error"):
        raise RuntimeError(str(data["error"]))
    key = next(k for k in data["result"] if k != "last")
    # Last candle is unfinished; never use it.
    return [(int(x[0]), float(x[4])) for x in data["result"][key][:-1]]

def step(state, history):
    if len(history) < 31:
        return
    timestamp, price = history[-1]
    if timestamp <= state.get("last_timestamp", 0):
        return
    previous_short = sum(p for _, p in history[-11:-1]) / 10
    previous_long = sum(p for _, p in history[-31:-1]) / 30
    current_short = sum(p for _, p in history[-10:]) / 10
    current_long = sum(p for _, p in history[-30:]) / 30
    signal = "HOLD"
    if previous_short <= previous_long and current_short > current_long and state["btc"] == 0:
        spend = state["cash"] * 0.1
        state["btc"] += spend * (1 - FEE) / price
        state["cash"] -= spend
        signal = "BUY"
    elif previous_short >= previous_long and current_short < current_long and state["btc"] > 0:
        state["cash"] += state["btc"] * price * (1 - FEE)
        state["btc"] = 0.0
        signal = "SELL"
    state["last_timestamp"] = timestamp
    if signal != "HOLD":
        state["trades"].append({"utc": dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).isoformat(), "action": signal, "price_usd": price})
    state["equity"] = state["cash"] + state["btc"] * price

def fresh():
    return {"cash": CASH, "btc": 0.0, "trades": [], "last_timestamp": 0, "equity": CASH}

def backtest(data):
    # Kraken OHLC provides at most 720 hourly rows, enough for 14 days + 30-hour warmup.
    cutoff = int((START - dt.timedelta(days=14)).timestamp())
    selected = [(t,p) for t,p in data if t <= int(START.timestamp())]
    first = next((i for i,(t,_) in enumerate(selected) if t >= cutoff), None)
    if first is None or first < 30:
        raise RuntimeError("Missing 30-hour warmup or 14-day history; cannot report valid replay")
    state = fresh()
    for i in range(first, len(selected)):
        step(state, selected[:i+1])
    first_price = selected[first][1]
    last_price = selected[-1][1]
    return {"period": "2026-10-08 through 2026-10-22 UTC", "starting_usd": CASH,
            "ending_equity_usd": round(state["equity"], 2),
            "profit_usd": round(state["equity"]-CASH,2),
            "buy_hold_equity_usd": round(CASH*last_price/first_price,2),
            "trades": state["trades"], "assumptions": "0.1% fee; no spread or slippage"}

def forward(data):
    now = dt.datetime.now(dt.timezone.utc)
    if now < START or now >= END:
        print("Outside forward test period; no trades.")
        return
    state = json.loads(STATE.read_text()) if STATE.exists() else fresh()
    eligible = [(t,p) for t,p in data if START.timestamp() <= t < END.timestamp()]
    # Process all missed completed candles, with earlier candles for warmup.
    for timestamp, _ in eligible:
        if timestamp > state["last_timestamp"]:
            history = [(t,p) for t,p in data if t <= timestamp]
            step(state, history)
    STATE.write_text(json.dumps(state, indent=2)+"\n")
    print(json.dumps({"equity_usd": round(state["equity"],2), "trades":len(state["trades"])},indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["backtest", "forward"])
    args = parser.parse_args()
    data = candles()
    if args.mode == "backtest":
        result = backtest(data)
        REPORT.write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps(result,indent=2))
    else:
        forward(data)
