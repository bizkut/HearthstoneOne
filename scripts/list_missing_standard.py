import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase
from card_generator.cache import EffectCache

def list_missing_standard():
    cache = EffectCache()
    CardDatabase.get_instance().load()
    standard_sets = ['TITANS', 'BATTLE_OF_THE_BANDS', 'WILD_WEST', 'WHIZBANGS_WORKSHOP', 'ISLAND_VACATION']
    
    missing = []
    for c in CardDatabase.get_collectible_cards():
        if c.card_set in standard_sets:
            if not cache.is_cached(c.card_id, c.card_set):
                # Only if it has text (other than just keywords)
                if c.text and len(c.text.strip()) > 5:
                    missing.append(c)
                    
    print(f"Total missing complex cards in Standard: {len(missing)}")
    for c in missing[:30]:
        print(f"{c.card_id}|{c.card_set}|{c.name}|{c.text}")

if __name__ == "__main__":
    list_missing_standard()
