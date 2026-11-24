import pandas as pd
import numpy as np
import re


def parse_weight_grams(val) -> float:
    if pd.isna(val):
        return np.nan
    s = str(val).lower().strip()
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if not m:
        return np.nan
    num = float(m.group(1))
    if "g" in s or "gram" in s:
        return num * 1.0
    if "kg" in s or "kilogram" in s:
        return num * 1000.0
    if "pound" in s or "lb" in s:
        return num * 453.592
    if "ounce" in s or "oz" in s:
        return num * 28.3495
    return num  # assume grams if unspecified
