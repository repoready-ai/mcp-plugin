"""Figure 2 (final): Welch two-sided per day, Holm-corrected."""
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
df = pd.read_csv("../data/growth.csv")
pvals = []
for day, g in df.groupby("day"):
    pvals.append(stats.ttest_ind(g[g.condition == "watered"].area_mm2, g[g.condition == "drought"].area_mm2, equal_var=False).pvalue)
order = sorted(range(len(pvals)), key=lambda i: pvals[i])
for rank, i in enumerate(order):
    pvals[i] = min(1, pvals[i] * (len(pvals) - rank))
s = df.groupby(["day", "condition"]).area_mm2.agg(["mean", "std"]).reset_index()
for cond, g in s.groupby("condition"):
    plt.errorbar(g.day, g["mean"], yerr=g["std"], label=cond)
plt.legend(); plt.savefig("../figures/fig2.pdf")
