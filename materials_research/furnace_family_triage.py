#!/usr/bin/env python3
"""Conservative high-temperature chemical-family triage, NOT stability simulation."""
import argparse, csv, re
from collections import Counter
ELEMENTS = re.compile(r'[A-Z][a-z]?')
HALOGENS={'F','Cl','Br','I'}
def main():
    p=argparse.ArgumentParser();p.add_argument('input_csv');p.add_argument('output_csv');a=p.parse_args()
    counts=Counter()
    with open(a.input_csv,newline='',encoding='utf-8-sig') as f,open(a.output_csv,'w',newline='',encoding='utf-8') as g:
        reader=csv.DictReader(f); fields=reader.fieldnames+['furnace_screen','reason','thermodynamic_stability','slag_erosion']
        writer=csv.DictWriter(g,fieldnames=fields);writer.writeheader()
        for row in reader:
            elems=set(ELEMENTS.findall(row.get('formula','')))
            family='lithium_metal_halide' if 'Li' in elems and (elems & HALOGENS) else 'other'
            reason='Lithium-metal halide; no established refractory oxide/carbide/nitride matrix' if family=='lithium_metal_halide' else 'Requires separate materials-family assessment'
            row.update(furnace_screen='not_prioritized' if family=='lithium_metal_halide' else 'needs_review',reason=reason,thermodynamic_stability='not_computed',slag_erosion='not_computed')
            counts[row['furnace_screen']]+=1;writer.writerow(row)
    print(dict(counts))
if __name__=='__main__':main()
