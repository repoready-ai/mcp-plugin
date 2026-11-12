"""Counting functions."""
import numpy as np
from skimage import measure


def count_stomata(mask, min_size=20):
    """Return the number of connected regions of at least `min_size` pixels in a binary mask."""
    labels = measure.label(mask > 0)
    sizes = np.bincount(labels.ravel())[1:]
    return int((sizes >= min_size).sum())


def density(n, mask, scale):
    """Stomata per mm² for a mask of pixel size `scale` mm."""
    return n / (mask.size * scale ** 2)
