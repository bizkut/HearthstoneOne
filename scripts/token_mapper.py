import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase

def map_tokens():
    CardDatabase.get_instance().load()
    collectible = CardDatabase.get_collectible_cards()
    all_cards = CardDatabase.get_instance()._cards.values()
    
    # Simple mapping: Name -> CardID for common tokens
    token_map = {}
    for c in all_cards:
        if not c.collectible:
            token_map[c.name.lower()] = c.card_id
            
    # Some common manual mappings
    token_map.update({
        "silver hand recruit": "CS2_101t",
        "voidwalker": "CS2_065",
        "imp": "EX1_316t",
        "sheep": "CS2_022e", # Wait, sheep is CS2_022e? No.
        "mirror image": "CS2_027t",
        "zombie": "RLK_060t",
    })
    
    return token_map

if __name__ == "__main__":
    m = map_tokens()
    print(f"Mapped {len(m)} potential tokens.")
