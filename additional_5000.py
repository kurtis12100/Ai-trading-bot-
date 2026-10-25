"""Additional 5,000 DISTINCT historical paper-only configurations, with fixed time split."""
import json
from pathlib import Path
from six_month_rsi_test import get_candles, START, END
from five_families_5000 import evaluate, FEE, SLIP

def main():
    raw, observed, expected = get_candles()
    rows = [(t, p, abs(p/raw[i-1][1]-1) if i else 0.0)
            for i, (t, p) in enumerate(raw)]
    begin, end = int(START.timestamp()), int(END.timestamp())
    split = begin + 122*86400
    families = ("trend_volatility", "bollinger", "macd", "regime", "volume")
    # Lookbacks differ from the previous 5,000 (5,7,9,12,15,18,21,24,27,30).
    lookbacks = (6,8,10,11,13,14,16,17,19,20)
    allocations = (0.025,0.05,0.10,0.15,0.20)
    results = {}
    for family in families:
        if family == "bollinger":
            thresholds=(0.5,0.8,1,1.2,1.5,1.8,2,2.2,2.5,3)
            variants=(0.5,0.8)
        elif family == "volume":
            thresholds=(1.2,1.4,1.6,1.8,2,2.2,2.5,3,3.5,4)
            variants=(0.002,0.005)
        elif family in ("trend_volatility","regime"):
            thresholds=(0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.01,0.012,0.015)
            variants=(0.001,0.003)
        else:
            thresholds=(0.0005,0.001,0.0015,0.002,0.0025,0.003,0.004,0.005,0.007,0.01)
            variants=(0.0005,0.002)
        configs=[(family,k,th,v,a) for k in lookbacks for th in thresholds for v in variants for a in allocations]
        assert len(configs)==1000
        best=None
        qualified=0
        for cfg in configs:
            training=evaluate(rows,cfg,begin,split)
            validation=evaluate(rows,cfg,split,end)
            candidate={"lookback":cfg[1],"threshold":cfg[2],"variant":cfg[3],
                       "allocation":cfg[4],"training":training,"validation":validation}
            if best is None or training["profit_usd"]>best["training"]["profit_usd"]:
                best=candidate
            if (training["profit_usd"]>0 and validation["profit_usd"]>0
                and training["trade_actions"]>=4 and validation["trade_actions"]>=4):
                qualified+=1
        results[family]={"tests":len(configs),"qualified_count":qualified,"best_training":best}
        print(family,"completed",len(configs),flush=True)
    report={"additional_tests":5000,"combined_with_previous":10000,
            "observed_hourly_candles":observed,"market":"BTC-USD",
            "fee_per_side":FEE,"slippage_per_side":SLIP,
            "warning":"Retrospective data and reused validation periods; not unseen forward data. Volume is a price-change proxy, not actual volume. No real trades.",
            "families":results}
    Path("additional_5000_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print("Finished 5,000 additional historical configurations")

if __name__=="__main__":
    main()
