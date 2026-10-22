"""One hundred distinct paper-only strategy trials. No exchange orders."""
import json
from pathlib import Path
from two_week_test import candles, START, FEE, CASH

def trial(data, short, long, allocation, fee=FEE):
    cutoff=int((START.replace() - __import__('datetime').timedelta(days=14)).timestamp())
    end=int(START.timestamp())
    rows=[(t,p) for t,p in data if t<=end]
    first=next((i for i,(t,_) in enumerate(rows) if t>=cutoff),None)
    if first is None or first<long: raise RuntimeError("Insufficient warmup history")
    cash=CASH; btc=0.; trades=0
    for i in range(first,len(rows)):
        ps=[p for _,p in rows[:i+1]]
        a=sum(ps[-short:])/short; b=sum(ps[-long:])/long
        pa=sum(ps[-short-1:-1])/short; pb=sum(ps[-long-1:-1])/long
        price=ps[-1]
        if pa<=pb and a>b and btc==0:
            spend=cash*allocation; btc=spend*(1-fee)/price; cash-=spend; trades+=1
        elif pa>=pb and a<b and btc>0:
            cash+=btc*price*(1-fee); btc=0.; trades+=1
    equity=cash+btc*rows[-1][1]
    return {"short":short,"long":long,"allocation":allocation,"equity_usd":round(equity,2),"profit_usd":round(equity-CASH,2),"trades":trades}

if __name__=="__main__":
    data=candles()
    configs=[(s,l,a) for s in (3,5,8,10,12,15,18,20,24,28) for l in (30,40,50,60,72) for a in (.05,.10)]
    results=[trial(data,*cfg) for cfg in configs]
    output={"note":"100 in-sample historical trials; not independent validation or a profit forecast","baseline_equity_usd":9935.40,"results":results}
    Path("strategy_trials.json").write_text(json.dumps(output,indent=2)+"\n")
    winners=sorted(results,key=lambda r:r["profit_usd"],reverse=True)
    output["profitable_count"]=sum(r["profit_usd"]>0 for r in results)
    output["best_in_sample"]=winners[0]
    Path("strategy_trials.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps({"profitable_count":output["profitable_count"],"best_in_sample":winners[0]},indent=2))
