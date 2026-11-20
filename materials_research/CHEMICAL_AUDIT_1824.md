# First chemical plausibility audit — 1,824 candidates (2026-11-20)

Recomputed directly from the recovered `materials_1824_priority.csv` file, **not** from the source's pre-existing `charge_check` flag.

| Metal | Count | Neutral under Li+ / M3+ / X− assumption | Ratio duplicates |
|---|---:|---:|---:|
| Y | 576 | 576 | 0 |
| Sc | 576 | 576 | 0 |
| In | 576 | 576 | 0 |
| La | 96 | 96 | 0 |
| **Total** | **1,824** | **1,824** | **0** |

Independent arithmetic: net formal charge = n(Li) + 3 n(M) − n(halide1) − n(halide2). All 1,824 equal zero **given the assumed trivalent metal**. All 1,824 are distinct after reduction by the greatest common divisor of element counts.

**Interpretation:** Formal charge neutrality is necessary for these simple ionic models but insufficient to establish synthesis, structural or thermodynamic stability, non-decomposition, safety, or rocket heat-shield performance. In can exhibit multiple oxidation states, and its +3 assumption needs special attention. The candidate set is dominated by lithium mixed halides; prioritize battery/solid electrolyte research, not rocket TPS. Next: literature/database cross-checks, oxidation state/coordination chemistry, decomposition-energy and phase-stability modeling, followed by experimental validation. No DFT or experimental thermal testing has been performed.
