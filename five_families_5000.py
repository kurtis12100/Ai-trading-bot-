"""Paper-only: 1000 configurations each across five new strategy families."""
import json, math, statistics
from pathlib import Path
from six_month_rsi_test import get_candles, START, END

CASH=10000.0
FEE=0.001
SLIP=0.0005

def sma(a,n):
    return sum(a[-n:])/n

def signal(prices, volumes, family, lookback, threshold, variant):
    if len(prices)<max(75,lookback*2+2): return 0
    p=prices[-1]
    slow=sma(prices,60)
    fast=sma(prices,lookback)
    returns=[prices[i]/prices[i-1]-1 for i in range(len(prices)-lookback+1,len(prices))]
    vol=statistics.pstdev(returns) if len(returns)>1 else 0
    if family=="trend_volatility":
        if vol>threshold: return -1
        return 1 if fast>slow*(1+variant) else -1
    if family=="bollinger":
        m=sma(prices,lookback); sd=statistics.pstdev(prices[-lookback:])
        z=(p-m)/sd if sd else 0
        return 1 if z < -threshold else -1 if z>variant else 0
    if family=="macd":
        short=sma(prices,lookback); long=sma(prices,lookback*2)
        strength=(short/long-1)
        return 1 if strength>threshold else -1 if strength < -variant else 0
    if family=="regime":
        trend=fast/slow-1
        if vol>threshold: return -1
        return 1 if trend>variant else -1 if trend < -variant else 0
    if family=="volume":
        baseline=sma(volumes[:-1],lookback)
        ratio=volumes[-1]/baseline if baseline else 0
        move=p/prices[-lookback-1]-1
        return 1 if ratio>threshold and move>variant else -1 if move < -variant else 0
    raise ValueError(family)

def evaluate(rows,cfg,begin,end):
    family,lookback,threshold,variant,allocation=cfg
    cash=CASH; btc=0.; actions=0; pending=0; peak=CASH; dd=0.
    prices=[r[1] for r in rows]; volumes=[r[2] for r in rows]
    last=None
    for i,(t,p,v) in enumerate(rows):
        if t<begin or t>=end: continue
        last=p
        if pending==1 and btc==0:
            spend=cash*allocation
            btc=spend*(1-FEE)/(p*(1+SLIP)); cash-=spend; actions+=1
        elif pending==-1 and btc>0:
            cash+=btc*p*(1-SLIP)*(1-FEE); btc=0.; actions+=1
        equity=cash+btc*p*(1-SLIP)*(1-FEE)
        peak=max(peak,equity); dd=max(dd,(peak-equity)/peak)
        pending=signal(prices[max(0,i-130):i+1],volumes[max(0,i-130):i+1],family,lookback,threshold,variant)
    if last is None: raise ValueError("Empty period")
    equity=cash+btc*last*(1-SLIP)*(1-FEE)
    return dict(profit_usd=round(equity-CASH,2),trade_actions=actions,max_drawdown_pct=round(dd*100,3))

def main():
    # Source supplies closing prices only; fetch Coinbase volume with identical candle windows.
    # For reproducibility and to avoid mismatched data requests, volume family uses a separate
    # price-movement proxy and is labelled explicitly in the report.
    from six_month_rsi_test import get_candles
    raw, observed, expected=get_candles()
    rows=[]
    for i,(t,p) in enumerate(raw):
        proxy=abs(p/raw[i-1][1]-1) if i else 0.0
        rows.append((t,p,proxy))
    begin=int(START.timestamp()); end=int(END.timestamp()); split=begin+122*86400
    families=("trend_volatility","bollinger","macd","regime","volume")
    lookbacks=(5,7,9,12,15,18,21,24,27,30)
    allocations=(0.025,0.05,0.1,0.15,0.2)
    summary={}
    for family in families:
        if family=="bollinger":
            thresholds=(0.5,0.8,1.0,1.2,1.5,1.8,2.0,2.2,2.5,3.0)
            variants=(0.5,0.8)
        elif family=="volume":
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
        results=[]
        for cfg in configs:
            tr=evaluate(rows,cfg,begin,split); va=evaluate(rows,cfg,split,end)
            results.append(dict(lookback=cfg[1],threshold=cfg[2],variant=cfg[3],allocation=cfg[4],training=tr,validation=va))
        ranked=sorted(results,key=lambda r:r["training"]["profit_usd"],reverse=True)
        qualified=[r for r in results if r["training"]["profit_usd"]>0 and r["validation"]["profit_usd"]>0 and r["training"]["trade_actions"]>=4 and r["validation"]["trade_actions"]>=4]
        summary[family]=dict(tests=1000,qualified_count=len(qualified),best_training=ranked[0],qualifying=qualified[:20])
        print(family, "complete",len(qualified),"qualified",flush=True)
    report=dict(total_tests=5000,market="BTC-USD",observed_hourly_candles=observed,
        fee_per_side=FEE,slippage_per_side=SLIP,
        execution="next hourly close approximation",
        data_note="Volume strategy uses absolute price-return proxy, NOT real traded volume. Do not interpret as volume validation.",
        validation_warning="Historical validation reused from earlier research, not independent unseen data. Configurations correlated and not proof of future returns.",
        families=summary)
    Path("five_families_5000_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:{'tests':v['tests'],'qualified_count':v['qualified_count'],'best_training':v['best_training']} for k,v in summary.items()},indent=2))
if __name__=="__main__": main()
