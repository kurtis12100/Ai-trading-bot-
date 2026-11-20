# Foundry lining R&D target and first test gates — 20 Nov 2026

## Agreed target
**50% longer usable service life** in a defined molten steel/iron foundry application, compared against the incumbent lining under matched chemistry, production cycle and end-of-life criteria. Also require no unacceptable metal contamination, slag penetration, cracking, or safety degradation.

## Completed analysis: illustrative economics
Baseline: 100 heats, USD $30,000 lining and replacement cost, no downtime costs included. Target: 150 heats. Baseline cost per heat = $300; target without coating premium = $200; benefit = $100/heat = 33.3% reduced material/reline cost per heat. With $5,000 extra application cost per reline, target = $233.33/heat, still 22.2% lower. Maximum premium at break-even is **$15,000 per 150-heat cycle**, holding all other costs fixed. These are hypothetical inputs and not an observed foundry cost. Run `python materials_research/lining_cost_model.py` to generate the full 30-row sensitivity scenario CSV.

## Screening matrix (no fabricated measured results)
- **Commercial alumina–magnesia spinel:** baseline for molten steel slag durability. Potential concerns: slag infiltration, thermal shock, metal retention.
- **Zirconia-rich protective surface:** compare non-wetting tendency; potential concerns: coating adhesion, phase stability, slag reaction and cost.
- **Commercial magnesia/magnesia-carbon lining:** application-specific incumbent, especially basic slag service; potential concerns: carbon oxidation or contamination.
None is established to extend life by 50% in the user's proposed service.

## Testing stages
1. **Desktop gate:** define metal grade, slag chemistry, typical peak temperature, whether crucible or ladle, current lining life, installed/repair cost and failure mode. Vendor data and published papers cannot be mixed as though test conditions match.
2. **Small laboratory coupons:** three or more independently produced specimens per baseline/control/candidate; molten steel contact-angle and retention measurements with atmosphere/oxygen activity controlled; SEM/EDS and XRD on penetrated samples.
3. **Slag-corrosion comparison:** professional lab adapted ASTM C874-20(2026) rotary slag method: https://store.astm.org/c0874-20r26.html . Laboratory chooses safe setup and compatibility.
4. **Thermal shock:** professional lab according to applicable ASTM C1171-16(2022): https://store.astm.org/c1171-16r22.html .
5. **Cost and safety:** fail if coating delaminates, causes inclusions or uncontrolled wear. Require favorable cost per heat at independently demonstrated service life before any real-world trial. Qualified furnace engineers decide whether in-service tests are appropriate.
6. **Novelty check before public recipe:** literature/patent search, written record, professional IP review; public GitHub only holds non-proprietary analysis.

**No actual molten-metal tests or thermodynamic crystal simulations have been run.** This deliverable documents economic scenario calculations and a validation plan.
