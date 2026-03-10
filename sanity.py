"""
sanity.py
Part of the "Pharmacophore Creation Strategies: Human vs. Machine" study.

Anh-Tien Ton et al. (2026)

This script calculates the McNemar contingency table and associated 
chi-squared values to compare human-generated vs. machine-generated models.
"""

# From https://rasbt.github.io/mlxtend/user_guide/evaluate/mcnemar/

import numpy as np
from mlxtend.evaluate import mcnemar

# 2 x 2 Contingency Table
# from DRD3 model_1 : U5 x model_2 : U4

tb_b = np.array([[13, 3466],
    [23,31028]])

chi2, p = mcnemar(ary=tb_b, corrected=True)
print('chi-squared:', chi2)
print('p-value:', p)
