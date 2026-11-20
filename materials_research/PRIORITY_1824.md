# Priority subset: 1,824 formulas (2026-11-20)

The original 51,000-formula preliminary screening CSV was recovered from the ChatGPT file library. It has 42,021 rows after composition-ratio deduplication. Exactly **1,824** rows have `screen = Review: compact, moderate lithium ratio`; 40,197 have the lower-priority label. The 1,824 label is a **formula-size heuristic**, not a measurement of thermal stability, heat-shield performance, patentability, or even synthesizability.

Example flagged formulas: Li1Y1Cl1Br3, Li1Y1Cl2Br2. These are lithium/metal halides originally generated as battery-oriented hypothetical compositions; halides are not a promising default for a rocket's exposed thermal-protection surface. Further screening should first test structural and charge plausibility, compare against known materials, and use appropriate thermodynamic databases. For rocket TPS, prioritize refractory oxides, carbides, nitrides, and oxidation-resistant composites in a *separate* candidate generation process.

To extract the exact subset from the full source CSV (when available locally):

```python
import pandas as pd
s = pd.read_csv('materials_51000_preliminary_screen.csv')
p = s[s['screen'].eq('Review: compact, moderate lithium ratio')]
assert len(p) == 1824
p.to_csv('materials_1824_priority.csv', index=False)
```
