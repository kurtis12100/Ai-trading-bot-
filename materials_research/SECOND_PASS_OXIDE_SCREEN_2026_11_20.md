# Second-pass screening of 2.5M hypothetical refractory oxides — 20 Nov 2026

## Reproducible result
Analyzed the **2,472,800 unique reduced formulas** from the previous enumerator, not 2.5 million independently established compounds. Counts after sequential, conservative filters:

| Filter | Remaining |
|---|---:|
| All distinct reduced formulas | 2,472,800 |
| Previously lower-chemistry-caution class (no Sn/Ce/Ti) | 488,378 |
| Aluminum, zirconium and silicon all included (within lower-caution group) | 49,456 |
| At most one of Hf, Sc, Yb, Lu, Gd (a *rough* cost/availability flag, not actual market prices) | 24,728 |
| Al + Zr collectively >= 50% of cations | 5,448 |
| Si <=20% of cations | **4,168** |

The 4,168 are an **arbitrary formulation-focused review pool, NOT proven more stable, cost-effective, novel or slag-resistant**. Five-metal mixing is not necessarily commercially desirable: phase separation and fabrication complexity are major concerns. No candidates have been validated as individual crystalline phases. Their formulas are not included in this public repository.

**Critical missing chemistry in original enumeration:** the list did not contain Mg, Ca, Cr or carbon-bearing architectures, despite practical MgAl2O4 spinel and MgO-C being relevant industrial baselines. Thus the search space itself is biased, and must NOT be considered comprehensive for steel foundries.

## External evidence and correction
A September 2026 experimental study reports no-cement in-situ spinel-forming alumina–magnesia castables with 5 wt% MgO outperforming tested low-cement alternatives in basic slag corrosion under its conditions. This is existing prior art, not ours: https://www.sciencedirect.com/science/article/pii/S0955221926002967

A review of magnesia-based refractories shows complex dissolution, penetration and reaction phase formation in steelmaking slags; charge neutrality cannot predict life: https://www.sciencedirect.com/science/article/pii/S1226086X24007366

The American Ceramic Society summarizes why alumina-spinel refractory performance depends on spinel content, penetration and corrosion: https://ceramics.org/ceramic-tech-today/ensuring-safe-production-of-metal-goods-a-review-of-alumina-spinel-castables-for-steel-ladles/

## Recommended change
Do NOT select 'winners' by speculative five-element formula ranking. Start a targeted **low-component** parallel design space using Al2O3, MgO/MgAl2O4, stabilized ZrO2 and application-specific additives/coatings. Define the molten steel composition, slag basicity, contact time and temperature. Then calculate equilibrium phases and reaction propensity using a validated thermodynamic dataset (CALPHAD/FactSage/Thermo-Calc) and cross-check against open literature before laboratory coupon studies.

The original 50% lifetime improvement remains an **unproven target**. No Gibbs energy/phase diagram calculations, density-functional simulations, wetting tests, physical corrosion tests or patent novelty checks were completed in this screen.
