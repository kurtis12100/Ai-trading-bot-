"""Compare the same 1000 predeclared paper strategies over six months.
First four months are training, final two months are validation.
"""
import json
from pathlib import Path
from six_month_rsi_test import get_candles, START, END
from strategy_trials import simulate

def main():
    rows, observed, expected = get_candles()
    begin = int(START.timestamp())
    end = int(END.timestamp())
    split = begin + 122 * 86400
    families = ("sma", "momentum", "mean_reversion", "breakout", "rsi")
    fasts = (3, 5, 7, 9, 12, 15, 18, 21, 24, 28)
    thresholds = (0.0, 0.001, 0.002, 0.004, 0.008)
    allocations = (0.025, 0.05, 0.10, 0.20)
    configs = [(f, k, max(30, k+2), t, a) for f in families for k in fasts for t in thresholds for a in allocations]
    assert len(configs) == 1000
    results = []
    for family, fast, slow, threshold, allocation in configs:
        cfg = (family, fast, slow, threshold, allocation)
        training = simulate(rows, cfg, begin, split)
        validation = simulate(rows, cfg, split, end)
        results.append({
            "family": family, "fast": fast, "slow": slow,
            "threshold": threshold, "allocation": allocation,
            "training": training, "validation": validation
        })
    ranked = sorted(results, key=lambda r: r["training"]["profit_usd"], reverse=True)
    best = ranked[0]
    active = [r for r in results if r["training"]["trades"] > 0 and r["validation"]["trades"] > 0]
    both_profitable = [r for r in active if r["training"]["profit_usd"] > 0 and r["validation"]["profit_usd"] > 0]
    output = {
        "market": "BTC-USD",
        "source": "Coinbase Exchange hourly candles",
        "start_utc": START.isoformat(),
        "end_utc": END.isoformat(),
        "training_end_utc": __import__("datetime").datetime.fromtimestamp(split, __import__("datetime").timezone.utc).isoformat(),
        "count": len(results),
        "observed_hourly_candles": observed,
        "expected_hourly_candles_approx": expected,
        "profitable_training_count": sum(r["training"]["profit_usd"] > 0 for r in results),
        "profitable_validation_count": sum(r["validation"]["profit_usd"] > 0 for r in results),
        "active_in_both_count": len(active),
        "profitable_in_both_count": len(both_profitable),
        "best_training_strategy": best,
        "best_training_strategy_validation_profit_usd": best["validation"]["profit_usd"],
        "fee_per_trade": 0.001,
        "spread_slippage_included": False,
        "selection_warning": "Best strategy is selected by training only. Validation is held out; testing 1000 configs still risks multiple comparisons. No forward profit established.",
        "results": results
    }
    Path("six_month_strategy_trials.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k:v for k,v in output.items() if k != "results"}, indent=2))

if __name__ == "__main__":
    main()
