"""Command line interface."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from .count import count_stomata, density


def main():
    p = argparse.ArgumentParser(description="Count stomata on mask files (.npy).")
    p.add_argument("masks", type=Path, help="folder of .npy masks")
    p.add_argument("--scale", type=float, required=True, help="mm per pixel")
    p.add_argument("--min-size", type=int, default=20, help="smallest region in pixels")
    p.add_argument("--out", type=Path, default=Path("densities.csv"), help="output CSV")
    a = p.parse_args()
    rows = []
    for f in sorted(a.masks.glob("*.npy")):
        m = np.load(f)
        n = count_stomata(m, a.min_size)
        rows.append({"file": f.name, "n": n, "density_mm2": density(n, m, a.scale)})
    pd.DataFrame(rows).to_csv(a.out, index=False)
