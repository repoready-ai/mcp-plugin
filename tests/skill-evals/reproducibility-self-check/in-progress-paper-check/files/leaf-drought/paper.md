# Drought slows leaf expansion through stomatal closure in *Arabidopsis*

A. Example, B. Sample. Preprint, 2026.

## Abstract
Under a 14-day drought, rosette leaves expanded 31 % more slowly than in watered
controls (Figure 2), stomatal density fell (Figure 3), and a logistic growth model
(Table 1) placed the slowdown after day 6.

## Methods
**Plants and drought.** 48 plants (24 per condition) grown 21 days, then watering was
withheld for 14 days in the drought group.

**Leaf area.** Rosettes were photographed daily; leaf area was measured in Fiji 2.14
(threshold "Default", scale 0.1 mm/px). Group means per day are compared with
**Welch's two-sided t-test** (unequal variances) at each day, Holm-corrected.

**Stomatal density.** Counted on segmentation masks of abaxial imprints (StomataNet
masks, one CSV per leaf), compared with a two-sided Mann-Whitney U test.

**Growth model.** A logistic curve was fitted to each group's mean leaf area with
scipy `curve_fit`; 95 % intervals from 1,000 bootstrap resamples of plants.

## Results
Figure 1. Experimental design (schematic).

Figure 2. Leaf area over 14 days, watered vs drought; mean ± SD; * Holm-corrected
Welch p < 0.05.

Figure 3. Stomatal density per mm², watered vs drought; Mann-Whitney U.

Table 1. Logistic growth parameters (K, r, t0) per condition with bootstrap 95 % CI.

## Code availability
Code is available at https://github.com/example-lab/leaf-drought.

## Data availability
Leaf-area and stomata tables are in the repository's data/ folder.
