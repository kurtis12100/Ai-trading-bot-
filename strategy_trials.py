"""1000 paper-only strategy configurations across five signal families."""
import json
import datetime as dt
from pathlib import Path
from two_week_test import candles, START, CASH, FEE

def signal(prices, family, fast, slow, threshold):
    if len(prices)<max(slow+2,fast+2): return 0
    p=prices[-1]
    if family=="sma":
        x=sum(prices[-fast:])/fast; y=sum(prices[-slow:])/slow
        return 1 if x>y*(1+threshold) else -1 if x<y*(1-threshold) else 0
    if family=="momentum":
        r=p/prices[-fast-1]-1
        return 1 if r>threshold else -1 if r< -threshold else 0
    if family=="mean_reversion":
        mean=sum(prices[-slow:])/slow
        r=p/mean-1
        return 1 if r< -threshold else -1 if r>threshold else 0
    if family=="breakout":
        prior=prices[-slow-1:-1]
        return 1 if p>max(prior)*(1+threshold) else -1 if p<min(prior)*(1-threshold) else 0
    if family=="rsi":
        diffs=[prices[i]-prices[i-1] for i in range(len(prices)-fast,len(prices))]
        gain=sum(max(d,0) for d in diffs); loss=sum(max(-d,0) for d in diffs)
        rsi=100*gain/(gain+loss) if gain+loss else 50
        bound=threshold*10000
        return 1 if rsi<50-bound else -1 if rsi>50+bound else 0
    raise ValueError(family)

def simulate(rows, config, begin, finish):
    family,fast,slow,threshold,allocation=config
    cash=CASH; btc=0.; trades=0
    prices=[p for _,p in rows]
    # Evaluate only after the requested start, with warmup before it.
    for i,(timestamp,price) in enumerate(rows):
        if timestamp<begin or timestamp>=finish: continue
        s=signal(prices[:i+1],family,fast,slow,threshold)
        if s==1 and btc==0:
            spend=cash*allocation; btc=spend*(1-FEE)/price; cash-=spend; trades+=1
        elif s==-1 and btc>0:
            cash+=btc*price*(1-FEE); btc=0.; trades+=1
    last=next((p for t,p in reversed(rows) if begin<=t<finish),None)
    if last is None: raise RuntimeError("No candles in evaluation period")
    equity=cash+btc*last
    return {"equity_usd":round(equity,2),"profit_usd":round(equity-CASH,2),"trades":trades}

if __name__=="__main__":
    rows=candles()
    end=int(START.timestamp()); begin=end-14*86400; split=begin+10*86400
    # 5 families x 10 lookbacks x 5 thresholds x 4 allocations = 1000.
    families=("sma","momentum","mean_reversion","breakout","rsi")
    fasts=(3,5,7,9,12,15,18,21,24,28)
    thresholds=(0.0,0.001,0.002,0.004,0.008)
    allocations=(0.025,0.05,0.10,0.20)
    configs=[(f,k,max(30,k+2),t,a) for f in families for k in fasts for t in thresholds for a in allocations]
    if len(configs)!=1000: raise RuntimeError("Expected 1000 configurations")
    results=[]
    for cfg in configs:
        training=simulate(rows,cfg,begin,split)
        validation=simulate(rows,cfg,split,end)
        results.append({"family":cfg[0],"fast":cfg[1],"slow":cfg[2],"threshold":cfg[3],"allocation":cfg[4],
                        "training":training,"validation":validation})
    ranked=sorted(results,key=lambda r:r["training"]["profit_usd"],reverse=True)
    best=ranked[0]
    output={"count":len(results),"training_days":10,"validation_days":4,
            "profitable_training_count":sum(r["training"]["profit_usd"]>0 for r in results),
            "profitable_validation_count":sum(r["validation"]["profit_usd"]>0 for r in results),
            "best_training_strategy":best,
            "note":"1000 in-sample selections with a held-out four-day validation; still not proof of future profitability. Paper only.",
            "results":results}
    Path("strategy_trials.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps({k:v for k,v in output.items() if k!="results"},indent=2))
