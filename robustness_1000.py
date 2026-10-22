"""Paper-only robustness sweep: 1000 distinct RSI/SMA configurations.
Signals use closed hourly bars; orders fill at the NEXT hourly close.
Training/validation are historical, not a fresh forward test.
"""
import json
from pathlib import Path
from six_month_rsi_test import get_candles, START, END
from strategy_trials import signal

FEE = 0.001
SLIPPAGE = 0.0005
INITIAL = 10000.0

def evaluate(rows, cfg, begin, end):
    family, fast, slow, threshold, allocation = cfg
    cash, units, trades, peak, drawdown = INITIAL, 0.0, 0, INITIAL, 0.0
    prices = [price for _, price in rows]
    pending = 0
    last_price = None
    for i, (ts, price) in enumerate(rows):
        if ts < begin or ts >= end:
            continue
        last_price = price
        # Execute the previous completed bar's signal, never the current bar's.
        if pending == 1 and units == 0:
            spend = cash * allocation
            units = spend * (1-FEE) / (price * (1+SLIPPAGE))
            cash -= spend
            trades += 1
        elif pending == -1 and units > 0:
            cash += units * price * (1-SLIPPAGE) * (1-FEE)
            units = 0.0
            trades += 1
        equity = cash + units * price * (1-SLIPPAGE) * (1-FEE)
        peak = max(peak, equity)
        drawdown = max(drawdown, (peak-equity)/peak)
        pending = signal(prices[max(0,i-60):i+1], family, fast, slow, threshold)
    if last_price is None:
        raise ValueError("No prices in period")
    equity = cash + units * last_price * (1-SLIPPAGE) * (1-FEE)
    return dict(profit_usd=round(equity-INITIAL,2), equity_usd=round(equity,2),
                trade_actions=trades, max_drawdown_pct=round(drawdown*100,3))

def main():
    rows, observed, expected = get_candles()
    begin, end = int(START.timestamp()), int(END.timestamp())
    split = begin + 122*86400
    # 2 families * 10 fast periods * 10 thresholds * 5 allocations = 1000
    fasts = (5,7,9,12,15,18,21,24,27,28)
    thresholds = (0.001,0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.010,0.012)
    allocations = (0.025,0.05,0.1,0.15,0.2)
    configs = [(family,fast,30,threshold,allocation)
               for family in ("rsi","sma")
               for fast in fasts for threshold in thresholds for allocation in allocations]
    assert len(configs)==1000
    results = []
    for cfg in configs:
        training = evaluate(rows,cfg,begin,split)
        validation = evaluate(rows,cfg,split,end)
        results.append(dict(family=cfg[0],fast=cfg[1],slow=cfg[2],
                            threshold=cfg[3],allocation=cfg[4],
                            training=training,validation=validation))
    both = [r for r in results if r["training"]["profit_usd"]>0
            and r["validation"]["profit_usd"]>0
            and r["training"]["trade_actions"]>=4
            and r["validation"]["trade_actions"]>=4]
    ranked = sorted(results,key=lambda r:r["training"]["profit_usd"],reverse=True)
    report = dict(count=1000, market="BTC-USD", observed_hourly_candles=observed,
                  fee_per_side=FEE,slippage_per_side=SLIPPAGE,
                  fill_model="next hourly close after signal; approximated",
                  profitable_both_with_min_4_actions=len(both),
                  best_by_training=ranked[0],
                  top_training=ranked[:10], qualifying=both,
                  warning="Validation period reused from earlier experiments; not independent unseen data. Candle-close fill approximation, not live execution.")
    Path("robustness_1000_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("qualifying","top_training")},indent=2))
if __name__=="__main__":
    main()
