#!/usr/bin/env python3
"""Scenario economics only: not a simulation of refractory chemistry or life."""
import csv
from pathlib import Path
def cost_per_heat(replacement_cost, life_heats, coating_cost=0, downtime_per_reline=0):
    return (replacement_cost+coating_cost+downtime_per_reline)/life_heats
def run():
    scenarios=[]
    baseline_life=100
    base_cost=30000
    for gain in [0,0.10,0.25,0.50,0.75,1.00]:
        life=baseline_life*(1+gain)
        for premium in [0,2500,5000,10000,15000]:
            baseline=cost_per_heat(base_cost,baseline_life)
            treated=cost_per_heat(base_cost,life,premium)
            scenarios.append(dict(life_improvement_pct=round(100*gain),baseline_heats=baseline_life,treated_heats=round(life),coating_premium_usd=premium,baseline_cost_per_heat_usd=round(baseline,2),treated_cost_per_heat_usd=round(treated,2),savings_per_heat_usd=round(baseline-treated,2),economic_break_even=treated<=baseline))
    path=Path(__file__).with_name("cost_scenarios.csv")
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=scenarios[0]); writer.writeheader();writer.writerows(scenarios)
    print("Wrote",path)
    print("At +50% life, before downtime savings, max break-even per-reline coating premium: $15,000 for illustrative $30k / 100-heat baseline")
if __name__=="__main__":run()
