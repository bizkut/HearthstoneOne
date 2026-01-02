import os
import sys
import re

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase
from card_generator.cache import EffectCache
from simulator import CardType

def cleanup_standard_keywords():
    cache = EffectCache()
    db = CardDatabase.load()
    standard_sets = ['TITANS', 'BATTLE_OF_THE_BANDS', 'WILD_WEST', 'WHIZBANGS_WORKSHOP', 'ISLAND_VACATION']
    
    keywords = ['Taunt', 'Rush', 'Charge', 'Divine Shield', 'Lifesteal', 'Windfury', 'Stealth', 'Poisonous', 'Reborn', 'Elusive', 'Discover']
    
    count = 0
    for c in CardDatabase.get_collectible_cards():
        if c.card_set in standard_sets:
            if cache.is_cached(c.card_id, c.card_set):
                continue
                
            text = c.text or ""
            # Strip HTML tags
            clean_text = re.sub(r'<.*?>', '', text)
            words = re.findall(r'\b\w+\b', clean_text)
            
            # If text is empty or only contains known simple keywords
            is_simple = not clean_text or all(w in keywords for w in words if len(w) > 2)
            
            if is_simple:
                # Cache as pass
                code = "def setup(game, source):\n    pass"
                cache.save_effect(c.card_id, code, c.card_set)
                count += 1
                
    print(f"Cleaned up {count} simple keyword-only cards in Standard.")

if __name__ == "__main__":
    cleanup_standard_keywords()
