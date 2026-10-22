"""Analyze six-month candidates; paper only."""
import json
from pathlib import Path
from six_month_rsi_test import get_candles, START, END
from strategy_trials import signal

def evaluate(rows, config, begin, finish):
    family, fast, slow, threshold, allocation = config
    cash, btc, peak, drawdown, trades = 10000., 0., 10000., 0., 0
    prices = [p for _, p in rows]
    for i, (ts, price) in enumerate(rows):
        if ts < begin or ts >= finish:
            continue
        s = signal(prices[:i+1], family, fast, slow, threshold)
        if s == 1 and btc == 0:
            spend = cash * allocation
            btc = spend * (1 - .001) / price
            cash -= spend
            trades += 1
        elif s == -1 and btc:
            cash += btc * price * (1 - .001)
            btc = 0.
            trades += 1
        equity = cash + btc * price
        peak = max(peak, equity)
        drawdown = max(drawdown, (peak - equity) / peak)
    return {"equity_usd": round(cash + btc * price, 2),
            "max_drawdown_pct": round(100 * drawdown, 3), "trades": trades}

def main():
    data = json.loads(Path("six_month_strategy_trials.json").read_text())
    rows, _, _ = get_candles()
    begin, end = int(START.timestamp()), int(END.timestamp())
    split = begin + 122 * 86400
    winners = [r for r in data["results"] if r["training"]["profit_usd"] > 0
               and r["validation"]["profit_usd"] > 0
               and r["training"]["trades"] > 0 and r["validation"]["trades"] > 0]
    analyzed = []
    for r in winners:
        cfg = (r["family"], r["fast"], r["slow"], r["threshold"], r["allocation"])
        analyzed.append({"config": dict(family=cfg[0], fast=cfg[1], slow=cfg[2],
                                        threshold=cfg[3], allocation=cfg[4]),
                         "training": evaluate(rows, cfg, begin, split),
                         "validation": evaluate(rows, cfg, split, end)})
    output = {"count": len(analyzed), "unique_signals": len(set(
        (r["family"], r["fast"], r["slow"], r["threshold"]) for r in winners)),
        "note": "Positive results are only eight allocation variants of two signal rules. Historical results do not establish profitability.",
        "candidates": analyzed}
    Path("candidate_risk_report.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
