"""Seven-day retrospective BTC comparison using identical hourly candles and strategies."""
import json
from datetime import datetime, timezone
from pathlib import Path
from comparison_paper import candles, signal, FEE, SLIPPAGE, ALLOCATION, START, NAMES

BEGIN=int(datetime(2026,10,18,tzinfo=timezone.utc).timestamp())
END=int(datetime(2026,10,25,tzinfo=timezone.utc).timestamp())

def run():
    rows=candles()
    if not rows or rows[0][0]>BEGIN-51*3600 or rows[-1][0]<END-3600:
        raise RuntimeError("Incomplete 51-hour warmup or Oct 18-24 hourly history; refusing partial results")
    summary={}
    for name in NAMES:
        cash=START;btc=0.;entry=None;trades=[];peak=START;max_dd=0.
        day="";day_start=START
        for i,(ts,price) in enumerate(rows):
            if ts<BEGIN or ts>=END:continue
            if i<51:raise RuntimeError("Missing warmup")
            current_day=datetime.fromtimestamp(ts,timezone.utc).date().isoformat()
            equity=cash+btc*price
            if day!=current_day:day,day_start=current_day,equity
            peak=max(peak,equity);max_dd=max(max_dd,(peak-equity)/peak)
            action=signal(name,[p for _,p in rows[:i+1]])
            if btc and entry and price<=entry*0.97:action="SELL"
            if equity<=day_start*0.98:action="SELL" if btc else "HOLD"
            if action=="BUY" and not btc and equity>day_start*0.98:
                spend=cash*ALLOCATION
                execution=price*(1+SLIPPAGE)
                btc=spend*(1-FEE)/execution;cash-=spend;entry=execution
                trades.append({"utc":ts,"side":"BUY","price":round(execution,2)})
            elif action=="SELL" and btc:
                execution=price*(1-SLIPPAGE)
                cash+=btc*execution*(1-FEE);btc=0.;entry=None
                trades.append({"utc":ts,"side":"SELL","price":round(execution,2)})
        final_price=next(p for t,p in reversed(rows) if t<END)
        final_equity=cash+btc*final_price*(1-SLIPPAGE)*(1-FEE)
        summary[name]={"ending_equity_usd":round(final_equity,2),
                       "profit_usd":round(final_equity-START,2),
                       "trade_actions":len(trades),
                       "completed_round_trips":sum(x["side"]=="SELL" for x in trades),
                       "max_drawdown_pct":round(max_dd*100,3),
                       "open_position":btc>0,"trades":trades}
    report={"period_utc":"2026-10-18 00:00 through 2026-10-24 23:00",
            "starting_usd_per_strategy":START,"results":summary,
            "assumptions":"Hourly candle-close simulated execution; 0.1% fee and 0.05% slippage each side; 10% cash allocation; close-based 3% stop; 2% UTC-day loss limit. Retrospective, not independent forward validation. No real orders."}
    Path("seven_day_comparison_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:{z:v[z] for z in ("profit_usd","trade_actions","max_drawdown_pct")} for k,v in summary.items()},indent=2))
if __name__=="__main__":run()
