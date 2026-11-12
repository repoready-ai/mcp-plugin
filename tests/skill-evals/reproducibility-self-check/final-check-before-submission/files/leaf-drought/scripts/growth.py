"""Figure 2: leaf area over time, watered vs drought."""
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv("data/growth.csv")
summary = df.groupby(["day", "condition"])["area_mm2"].agg(["mean", "std"]).reset_index()
pvals = []
for day, g in df.groupby("day"):
    a = g[g.condition == "watered"].area_mm2
    b = g[g.condition == "drought"].area_mm2
    pvals.append(stats.ttest_ind(a, b, equal_var=False).pvalue)  # Welch, two-sided
# Holm correction
order = sorted(range(len(pvals)), key=lambda i: pvals[i])
for rank, i in enumerate(order):
    pvals[i] = min(1, pvals[i] * (len(pvals) - rank))
for cond, g in summary.groupby("condition"):
    plt.errorbar(g.day, g["mean"], yerr=g["std"], label=cond)
plt.legend(); plt.savefig("figures/fig2.pdf")
