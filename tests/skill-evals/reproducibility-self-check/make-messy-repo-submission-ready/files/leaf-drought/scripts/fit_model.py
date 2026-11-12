"""Table 1: logistic growth parameters with bootstrap CIs."""
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

def logistic(t, K, r, t0):
    return K / (1 + np.exp(-r * (t - t0)))

df = pd.read_csv("data/growth.csv")
for cond, g in df.groupby("condition"):
    m = g.groupby("day").area_mm2.mean()
    p, _ = curve_fit(logistic, m.index, m.values, p0=[300, 0.5, 7])
    plants = g.plant.unique()
    boots = []
    for _ in range(1000):
        pick = np.random.choice(plants, len(plants))
        mb = g[g.plant.isin(pick)].groupby("day").area_mm2.mean()
        boots.append(curve_fit(logistic, mb.index, mb.values, p0=p)[0])
    lo, hi = np.percentile(boots, [2.5, 97.5], axis=0)
    print(cond, p, lo, hi)
