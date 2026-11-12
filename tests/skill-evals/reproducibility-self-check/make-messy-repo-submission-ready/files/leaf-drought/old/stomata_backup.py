"""Figure 3: stomatal density."""
import pandas as pd
from scipy import stats

counts = pd.read_csv("data/stomata.csv")
masks = pd.read_csv("/Users/anna/Desktop/stomata_masks/masks_summary.csv")
dens = counts.merge(masks, on="leaf_id")
dens["density"] = dens["n_stomata"] / dens["mask_area_mm2"]
w_ = dens[dens.condition == "watered"].density
d_ = dens[dens.condition == "drought"].density
print(stats.mannwhitneyu(w_, d_, alternative="two-sided"))
