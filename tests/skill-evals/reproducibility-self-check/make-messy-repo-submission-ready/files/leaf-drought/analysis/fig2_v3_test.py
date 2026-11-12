# trying mann-whitney instead, not used in the paper
import pandas as pd
from scipy import stats
df = pd.read_csv("../data/growth.csv")
for day, g in df.groupby("day"):
    print(day, stats.mannwhitneyu(g[g.condition == "watered"].area_mm2, g[g.condition == "drought"].area_mm2).pvalue)
