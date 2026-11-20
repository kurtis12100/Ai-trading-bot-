#!/usr/bin/env python3
"""Conservative formula triage; does not predict thermal stability."""
import csv, re, sys, math
from collections import Counter
from pathlib import Path
PATTERN = re.compile(r"([A-Z][a-z]?)([0-9]*)")
OX = {"Li":1,"Na":1,"K":1,"Mg":2,"Ca":2,"Al":3,"Y":3,"La":3,"Sc":3,"Zr":4,"Hf":4,"Ti":4,"F":-1,"Cl":-1,"Br":-1,"I":-1,"O":-2,"N":-3}
HALOGENS = {"F","Cl","Br","I"}
def parse(formula):
    parts = PATTERN.findall(formula)
    if not parts or "".join(a+b for a,b in parts) != formula: raise ValueError("Unsupported formula")
    counts=Counter()
    for element,number in parts:
        counts[element]+=int(number or 1)
    if any(v<=0 for v in counts.values()): raise ValueError("Nonpositive count")
    return counts
def reduced(c):
    g=math.gcd(*c.values())
    return "".join(f"{k}{c[k]//g}" for k in sorted(c))
def assess(formula):
    c=parse(formula)
    unknown=sorted(set(c)-set(OX))
    charge=None if unknown else sum(OX[e]*n for e,n in c.items())
    return {"reduced_formula":reduced(c),"atom_count":sum(c.values()),"charge_balance":("unknown" if charge is None else "yes" if charge==0 else "no"),"contains_halogen":bool(set(c)&HALOGENS),"unsupported_elements":",".join(unknown),"high_temp_tps_flag":("halide-rich: thermal suitability unverified" if set(c)&HALOGENS else "thermal suitability unverified")}
def main(path):
    src=Path(path)
    with src.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames: raise SystemExit("CSV missing header")
        col=next((x for x in reader.fieldnames if x.lower() in ("formula","composition","chemical_formula")),None)
        if not col: raise SystemExit("No formula/composition column; columns: "+str(reader.fieldnames))
        seen=set()
        out=src.with_name(src.stem+"_validated.csv")
        with out.open("w",newline="",encoding="utf-8") as g:
            fields=list(reader.fieldnames)+["parsed","reduced_formula","duplicate_reduced","atom_count","charge_balance","contains_halogen","unsupported_elements","high_temp_tps_flag","error"]
            writer=csv.DictWriter(g,fieldnames=fields,extrasaction="ignore");writer.writeheader()
            for row in reader:
                formula=(row.get(col) or "").strip()
                try:
                    a=assess(formula); dup=a["reduced_formula"] in seen;seen.add(a["reduced_formula"])
                    writer.writerow({**row,**a,"parsed":"yes","duplicate_reduced":str(dup).lower(),"error":""})
                except Exception as e:
                    writer.writerow({**row,"parsed":"no","error":str(e)})
    print("Saved",out)
if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("Usage: python screen.py input.csv")
    main(sys.argv[1])
