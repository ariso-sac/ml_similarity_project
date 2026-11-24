import ast
import re
import pandas as pd

VALID_COLORS = {
    'black', 'white', 'grey', 'gray', 'blue', 'navy blue', 'navy', 'royal blue', 
    'sky blue', 'airforce blue', 'air force blue', 'ink blue', 'steel blue', 
    'peacock blue', 'indian blue', 'imperial blue', 'medieval blue', 'ceil blue', 
    'galaxy blue', 'turquoise', 'aqua', 'firozi', 'teal', 'red', 'maroon', 
    'burgundy', 'wine', 'rust', 'coral', 'pink', 'baby pink', 'peach', 'gajri', 
    'rani', 'magenta', 'fuchsia', 'strawberry', 'rose', 'onion', 'green', 
    'bottle green', 'olive', 'olive green', 'light green', 'dark green', 
    'peacock green', 'pista', 'mehandi', 'emerald', 'hunter', 'fluid green', 
    'composed green', 'yellow', 'mustard', 'gold', 'golden', 'lemon', 
    'orange', 'purple', 'violet', 'lavender', 'eggplant', 'grape', 'brown', 
    'chocolate', 'coffee', 'camel', 'khaki', 'beige', 'chiku', 'skin', 
    'off white', 'cream', 'silver', 'charcoal', 'indigo', 'multicolor'
}

# 2. Typo & spelling normalization map based on your specific column values
TYPO_MAP = {
    'blackk': 'black', 'black1': 'black', 'black2': 'black',
    'maroonn': 'maroon', 'mehroon': 'maroon', 'marun': 'maroon',
    'orangee': 'orange', 'royall': 'royal blue', 'yelloww': 'yellow',
    'nabyblue': 'navy blue', 'purpel': 'purple', 'musterd': 'mustard',
    'magneta': 'magenta', 'lavander': 'lavender', 'bege': 'beige',
    'fuschia': 'fuchsia', 'turquoises': 'turquoise', 'gray': 'grey',
    'inkblue': 'ink blue', 'skyblue': 'sky blue', 'off-white': 'off white',
    'multicolour': 'multicolor', 'multi-coloured': 'multicolor', 
    'multi coloured': 'multicolor', 'multi-colored': 'multicolor'
}

def parse_colours(cell):
    # Parse stringified list into actual list
    if isinstance(cell, str):
        try:
            items = ast.literal_eval(cell)
        except (ValueError, SyntaxError):
            items = [cell]
    elif isinstance(cell, list):
        items = cell
    else:
        return []

    extracted = []
    for item in items:
        if not item or not str(item).strip():
            continue
        
        text = str(item).lower()
        # Normalize typos before matching
        for wrong, right in TYPO_MAP.items():
            text = re.sub(rf'\b{wrong}\b', right, text)
            
        # Sort colors by length descending so 'navy blue' matches before 'blue'
        for color in sorted(VALID_COLORS, key=len, reverse=True):
            if re.search(rf'\b{re.escape(color)}\b', text):
                formatted = color.title()
                if formatted not in extracted:
                    extracted.append(formatted)
                # Remove matched color so 'navy blue' doesn't also trigger 'blue'
                text = re.sub(rf'\b{re.escape(color)}\b', '', text)

    return extracted
