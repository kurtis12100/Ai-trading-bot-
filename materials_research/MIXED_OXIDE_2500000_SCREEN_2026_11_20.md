# 2.5-million mixed-oxide exploration — 20 November 2026

## Actual computation completed
A reproducible local Python enumeration generated **2,500,000** nominal five-cation oxide compositions. Each of 800 deterministic, distinct metal sets was combined with 3,125 ratio choices (1–5 for each cation). Metals: Al(III), Sc(III), Y(III), La(III), Gd(III), Yb(III), Lu(III), Zr(IV), Hf(IV), Ti(IV), Ce(IV), Sn(IV), Si(IV). Oxygen stoichiometry used formal oxidation-state neutrality, followed by formula reduction and duplicate removal.

- Raw combinations enumerated: **2,500,000**
- Distinct reduced formulas: **2,472,800**
- Duplicate reduced formulations: **27,200**
- Lower-caution *review* group (no Sn, Ce, Ti in five-cation set): **488,378**
- Extra chemistry-caution group (includes Sn/Ce/Ti): **1,984,422**

**Crucial caveat:** Lower-caution *does not* mean more stable, safe, synthesizable, novel, or useful. Sn/Ce/Ti caution is only a coarse redox/processing flag, and the remaining constituents also have substantial unknowns. Oxygen stoichiometry is an assumed nominal valence assignment, not an observed stable compound. Mixed five-cation oxides may segregate rather than form a single phase.

## Results and limits
No density-functional theory, phase diagram / Gibbs free energy, slag-contact kinetics, wetting angle, melting point, mechanical lifetime or laboratory testing was performed. **Zero compounds have been demonstrated to deliver the 50% longer lining-life target.** Novelty/patents have not been checked for the generated formulas. This is an automated composition space enumeration, not evidence of discovery.

Generated companion files in current ChatGPT session: `refractory_2500000_formulas.csv.gz` (2,472,800 unique rows), `priority_examples.csv`, `scan.py`, `results.json`. Files are not stored in this public GitHub repository: unpublished candidate data should not be published before an intellectual property review.

## Recommended next scientific steps
1. Choose specific molten steel grade and slag chemistry, oxygen activity, temperature, furnace/casting geometry and incumbent lining.
2. Prioritize **known low-component ceramic baselines** (stabilized ZrO2, Al2O3–MgAl2O4, MgO–C) before interpreting highly complex 5-cation formulas; 5-cation mixtures are harder to manufacture and validate.
3. Reduce the formula set further using cost, risk and existing measured phase stability; compare against materials databases and patents. No ungrounded numerical 'stability probability' should be assigned.
4. Run CALPHAD/DFT or thermodynamic equilibrium with appropriate verified databases to model solid phases and slag reactions, then lab coupon tests with matched baselines and replicates. An oxide being charge-neutral does not show slag resistance or a non-wetting effect.

**Status:** Enumeration and basic bookkeeping screen completed, not material performance testing.
