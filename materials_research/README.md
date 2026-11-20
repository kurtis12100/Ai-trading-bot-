# Materials screening (separate from trading bot)

This folder is an independent research project. It does not change the trading bot.

Place the original `materials_51000_preliminary_screen.csv` in this folder, then run:

```bash
python materials_research/screen.py materials_research/materials_51000_preliminary_screen.csv
```

The screen checks composition parsing, reduced-form duplicates and simple oxidation-state charge balance. These are *heuristics*, not measurements of thermodynamic stability, manufacturability, novelty, or suitability for rocket thermal protection. Lithium/halide compositions are not automatically plausible high-temperature heat shields. Follow-up requires materials database comparisons and physical-property calculations.
