# Stoichiometric spinel potential — 20 Nov 2026

A reproducible local Python mass-balance test was completed on **all 1,771** Al2O3/MgO/ZrO2/SiO2 blend ratios and the **94** previously shortlisted compositions.

Reaction used for the bookkeeping upper bound: MgO + Al2O3 → MgAl2O4. For each 100 g nominal blend, reacted moles = min(mass(MgO)/40.3044, mass(Al2O3)/101.9613). Potential spinel mass = reacted moles × 142.2657; calculate remaining Al2O3 and MgO separately. Assumes full completion of this isolated reaction, and ignores competing phases, slag attack, kinetics, glass, temperature, atmosphere, sintering and porosity.

Results:
- Original grid: **1,771** mixtures; **231** have no SiO2.
- Review subset: **94** mixtures; **32** have no SiO2.
- Of the 32 silica-free review mixtures, **23** have a theoretical spinel mass >=50 wt% under the deliberately optimistic reaction-only assumption.
- Maximum calculated spinel across the shortlist: **97.67 wt%**, for nominal 70 wt% Al2O3 + 30 wt% MgO, with calculated residual 2.33 wt% MgO. **This is a known spinel-forming chemistry, not a new invention.**
- Another example, nominal 65 Al2O3 / 25 MgO / 10 ZrO2 / 0 SiO2, has 88.245 wt% theoretical spinel plus 1.755 wt% excess Al2O3 and 10 wt% ZrO2. This does NOT imply the zirconia is stabilized or the phases coexist under service conditions.

**Interpretation:** This is an actual compositional stoichiometry calculation, not a thermodynamic equilibrium simulation or validation of reduced molten-steel wetting or slag corrosion. None of the 94 compositions has been shown to last 50% longer.

**Next decisive computational test:** equilibrium phases and interfacial reactions at a defined melt composition, oxygen potential, and slag basicity using a thermochemical database. Without validated temperature-dependent Gibbs-energy models, numerical stability rankings would be invented. Laboratory trials would then be required.
