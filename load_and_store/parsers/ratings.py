import pandas as pd
import numpy as np
import re

def parse_rating(val) -> float:
    if pd.isna(val):
        return np.nan
    m = re.search(r"(\d+(?:\.\d+)?)", str(val))
    return float(m.group(1)) if m else np.nan