# stomacount

Count stomata on segmentation masks of leaf imprints and report density per mm².

## Install
    pip install .

## Usage
    stomacount masks/ --scale 0.1 --out densities.csv

Options: `--scale` (mm per pixel), `--min-size` (pixels, default 20), `--out` (CSV path).
