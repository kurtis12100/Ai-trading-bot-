"""Educational BTC/USD paper-trading bot. No exchange orders or credentials."""
import json
import time
import urllib.request
from pathlib import Path

STATE = Path("paper_state.json")
STARTING_CASH = 10000.0
FEE = 0.001
SHORT_WINDOW = 10
LONG_WINDOW = 30

def prices():
    url = "https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=60"
    with urllib.request.urlopen(url, timeout=15) as response:
        payload = json.load(response)
    if payload.get("error"):
        raise RuntimeError(str(payload["error"]))
    key = next(iter(payload["result"].keys() - {"last"}))
    # Exclude the latest unfinished candle.
    return [float(row[4]) for row in payload["result"][key][:-1]]

def run_once():
    closes = prices()
    if len(closes) < LONG_WINDOW + 1:
        raise RuntimeError("Insufficient candles")
    previous_short = sum(closes[-SHORT_WINDOW-1:-1]) / SHORT_WINDOW
    previous_long = sum(closes[-LONG_WINDOW-1:-1]) / LONG_WINDOW
    current_short = sum(closes[-SHORT_WINDOW:]) / SHORT_WINDOW
    current_long = sum(closes[-LONG_WINDOW:]) / LONG_WINDOW
    price = closes[-1]
    state = json.loads(STATE.read_text()) if STATE.exists() else {
        "cash": STARTING_CASH, "btc": 0.0, "last_candle": None
    }
    # One decision per completed candle, even across restarts.
    candle = len(closes), closes[-1]
    if state["last_candle"] == list(candle):
        print("Already processed latest candle")
        return
    signal = "HOLD"
    if previous_short <= previous_long and current_short > current_long and state["btc"] == 0:
        # Allocate at most 10% of available cash.
        spend = state["cash"] * 0.10
        state["btc"] += spend * (1 - FEE) / price
        state["cash"] -= spend
        signal = "PAPER BUY"
    elif previous_short >= previous_long and current_short < current_long and state["btc"] > 0:
        state["cash"] += state["btc"] * price * (1 - FEE)
        state["btc"] = 0.0
        signal = "PAPER SELL"
    state["last_candle"] = list(candle)
    STATE.write_text(json.dumps(state, indent=2))
    print(f"{signal}: BTC ${price:,.2f}; simulated equity ${state['cash'] + state['btc'] * price:,.2f}")

if __name__ == "__main__":
    run_once()
