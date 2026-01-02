import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase
from card_generator.cache import EffectCache

def implementation_audit():
    cache = EffectCache()
    CardDatabase.get_instance().load()
    cards = CardDatabase.get_collectible_cards()
    
    implemented = 0
    keyword_only = 0
    missing = 0
    
    keywords = ["Taunt", "Divine Shield", "Rush", "Charge", "Windfury", "Stealth", "Poisonous", "Lifesteal", "Reborn"]
    
    for c in cards:
        if cache.is_cached(c.card_id, c.card_set):
            implemented += 1
        elif not c.text:
            keyword_only += 1
        else:
            # Check if text is just a combination of keywords
            text = c.text.replace("<b>", "").replace("</b>", "").replace(".", "").strip()
            words = [w.strip() for w in text.split(",")]
            if all(any(k.lower() == w.lower() for k in keywords) for w in words if w):
                keyword_only += 1
            else:
                missing += 1
                
    print(f"Total Collectible Cards: {len(cards)}")
    print(f"Implemented with code: {implemented}")
    print(f"Implemented via keywords only: {keyword_only}")
    print(f"TOTAL PLAYABLE: {implemented + keyword_only}")
    print(f"Missing: {missing}")

if __name__ == "__main__":
    implementation_audit()
