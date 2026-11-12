# exploratory PCA of leaf shape, not in the paper
import numpy as np
print(np.linalg.svd(np.random.rand(10, 3))[1])
