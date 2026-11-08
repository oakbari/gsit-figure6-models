# Four-panel Figure 6 for generic ngSIT performance

This repository reproduces **one selected four-panel figure**. It contains the
model source, plotting code, equations, legend, parameter definitions, numerical
grid values and checks associated with that figure.

All parameters are illustrative. No experimental observations, strain-specific
fitness estimates or fitted ecological parameters are used.

## Reproduce the figure

Tested with Python 3.12.14. Install the pinned dependencies and run:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python reproduce.py
```

The last command runs eight tests, including 1,000 randomized adult-target
checks, regenerates Figure 6, and compares all four numerical grids with saved
references. Outputs appear in `results/`:

- `Figure_6.pdf`: vector artwork, 705 × 550 points.
- `Figure_6.svg`: editable vector artwork.
- `Figure_6.png`: 600 dpi raster artwork, approximately 9.79 × 7.64 inches.
- `selected_panel_A.csv` through `selected_panel_D.csv`: generated model values.
- `software_versions.json`: software versions used for the run.

Only package installation requires internet access. No accounts, credentials,
experimental source data, Word software or manuscript access are required.
Run just the analytic checks with `python -m unittest -v test_figure6`.

## Figure panels and parameters

| Panel | Axes and conditions | Color represents |
| --- | --- | --- |
| A | c = 0–1; released/wild male ratio r = 0–50; f = 0 | Reproductive-output reduction (%) |
| B | c = 0–1; relative fertility f = 0–20%; r = 10 | Reproductive-output reduction (%) |
| C | c = 0–1; f = 0–1%; illustrative R0 = 4 | Maintained ratio for 99% equilibrium adult-female suppression |
| D | c = 0–1; R0 = 2–10; f = 0 | Maintained ratio for the same 99% adult-female target |

Every heat map uses a 100 × 100 cell-centered grid. Percent-valued axes show
`100*f`; the CSV files store `f` as a fraction. `c` is relative mating
competitiveness, not a general measure of organismal fitness. `R0` is the
low-density number of adult daughters per female without intervention, not an
epidemiological reproduction number.

Panels A–B use a shared linear color scale from 0 to 100% reproductive reduction.
Panels C–D use a shared logarithmic ratio scale. Ratios <=1 or >=1000 use the
respective end color; CSV values remain uncapped. Panel C ends at 1% fertility, below the approximately 25.19% feasibility boundary; the infeasible region is outside the displayed range.
Contours are analytic. Exact axis endpoints, including the infeasible c=0
boundary for positive targets, are defined by the equations rather than sampled
as cell-center values.

## Models

Relative reproductive output:

```text
G = (1 + c*r*f)/(1 + c*r)
reproductive reduction = 1 - G
```

Illustrative density-regulated recruitment:

```text
F_next = R0*G*F/[1 + (R0 - 1)*G*F/K]
F_star/K = max(0, (R0*G - 1)/[(R0 - 1)*G])
```

For target equilibrium adult fraction `a=0.01`, define `H=R0-a*(R0-1)`:

```text
r_a = (H - 1)/[c*(1 - H*f)]
```

A finite target requires `c>0` and `f<1/H`; maintaining `r>=r_a` gives the target
in this model. In Panel C, `H=3.97` and the fertility feasibility boundary is
`f=1/3.97`, approximately 25.19%. In Panel D, `f=0`, so
`r_a=0.99*(R0-1)/c`. The full mathematical description is in
`docs/Figure_6_equations.tex` and the manuscript-style caption in
`docs/Figure_6_legend.md`.

## Interpretation and limits

The mating model assumes random effective mating, one effective mating per
female, and equal fecundity across mate classes. Fertility is relative
viable-offspring output following a released-male mating. It is not a parental
sorting-error rate. It equals a fully fertile contaminant fraction only when
fertile and sterile release males have equal mating weights and all other males
are completely sterile.

The population panels assume a maintained ratio of males actually available to
mate, no immigration, and constant parameters. Density compensation acts on
viable recruitment. Spatial and age structure, seasonality, dormant eggs,
stochasticity and explicit construct inheritance are omitted. Descendants are
aggregated as fertile residents. Equilibrium adult suppression is distinct from
single-cohort reproductive reduction, extinction probability, release frequency
and required production throughput. None of those latter quantities is inferred.

## Repository contents

| Path | Purpose |
| --- | --- |
| `models.py` | Shared model equations and domain checks |
| `scripts/generate_figure6.py` | Source for this four-panel figure and its grids |
| `test_figure6.py` | Analytic boundaries, examples, response directions and equilibrium checks |
| `reproduce.py` | Tests, figure generation and reference comparisons |
| `references/` | Four saved model grids for reproducibility checks |
| `results/` | This figure in three formats and its generated values |
| `docs/Figure_6_legend.md` | Complete figure legend |
| `docs/Figure_6_equations.tex` | Equations, derivation and assumptions |
| `docs/PUBLICATION.md` | Upload and publication metadata instructions |

The reference CSVs are computed model values, not empirical measurements.
Numerical comparisons use tolerance `1e-10`. PDF metadata may vary between runs;
byte-identical PDF serialization is not required. A feasibility margin within
eight machine epsilons of zero is treated as its analytic boundary.

## Attribution and publication metadata

The source and figure were developed with OpenAI Codex assistance. The
reproductive and population models are introduced and derived in the ngSIT
manuscript and in `docs/Figure_6_equations.tex`. Final manuscript bibliographic
details will be supplied by the authors. The population extension uses Beverton–Holt-type saturation;
see Beverton and Holt, *On the Dynamics of Exploited Fish Populations*,
[reprint DOI](https://doi.org/10.01007/978-94-011-2106-4). No empirical values were
transferred from that source.

Repository: [https://github.com/oakbari/gsit-figure6-models](https://github.com/oakbari/gsit-figure6-models).

Author names, the final manuscript citation and an author-approved license remain
to be added. This repository does not assign a software license.

Panel C uses a mixture interpretation: f is the fully fertile fraction of the final release cohort. Remaining released males are completely sterile. Both released classes have equal mating competitiveness, and fertile contaminants have wild-type fertility. No empirical contamination rate is assumed.

This presentation revision uses short panel titles, explicit ratio color-bar ticks and a marked analytic example in panel C. The legend explains the question answered by each panel. The model and all four numerical grids are unchanged.

Readable artwork revision: shortened titles and example callout; larger axis, tick and contour labels. Assumptions and interpretation are retained in the legend rather than figure footnotes. Numerical grids are unchanged.
