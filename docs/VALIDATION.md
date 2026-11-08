# Validation of the four-panel Figure 6 package

Prepared and validated on 8 November 2026 with Python 3.12.14 and the pinned
dependencies. `python reproduce.py` passes:

- Eight tests specific to the selected figure.
- One thousand randomized population-target inversions and equilibrium checks.
- Reproductive-contour and exact feasibility-boundary checks.
- Population-growth sweep formula and response-direction checks.
- Comparisons with all four saved numerical grids at tolerance `1e-10`.
- PDF, SVG and 600 dpi PNG generation for one four-panel Figure 6.

The generated artwork matches the selected figure. The archive was checked for
integrity and reproduced from a separate extracted folder. No earlier figures,
alternative analyses, Word review drafts or experimental datasets are required.

The public repository is https://github.com/oakbari/gsit-figure6-models.
Validation reported here was run locally; no hosted GitHub tests have run.
Author names, final citations and an approved license remain to be supplied
by the authors.
