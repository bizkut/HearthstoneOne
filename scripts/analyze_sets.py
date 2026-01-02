import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase
from card_generator.cache import EffectCache

def analyze_unimplemented():
    cache = EffectCache()
    CardDatabase.get_instance().load()
    cards = CardDatabase.get_collectible_cards()
    
    unimplemented_by_set = {}
    
    for c in cards:
        if not cache.is_cached(c.card_id, c.card_set):
            unimplemented_by_set[c.card_set] = unimplemented_by_set.get(c.card_set, 0) + 1
            
    # Sort by number of unimplemented cards
    sorted_sets = sorted(unimplemented_by_set.items(), key=lambda x: x[1], reverse=True)
    
    print("Unimplemented collectible cards by set:")
    for card_set, count in sorted_sets:
        print(f"{card_set}: {count}")

if __name__ == "__main__":
    analyze_unimplemented()
