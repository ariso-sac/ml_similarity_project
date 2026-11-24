import pandas as pd
import numpy as np
import re

def parse_price(val) -> float:
    if pd.isna(val):
        return np.nan
    s = str(val).replace(",", "")
    nums = re.findall(r"\d+(?:\.\d+)?", s)
    if not nums:
        return np.nan
    # If range like "$10.00 - $20.00", take midpoint
    floats = [float(n) for n in nums[:2]]
    return float(np.mean(floats))