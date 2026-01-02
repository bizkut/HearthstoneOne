import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase, Race, CardType
from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache

def bulk_alias_sync():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    CardDatabase.get_instance().load()
    cards = CardDatabase.get_collectible_cards()
    
    # Map of base_id -> effect_code (for cards we already have)
    # or base_id -> extension
    
    alias_prefixes = ["CORE_", "VAN_", "CS3_"]
    
    count = 0
    for c in cards:
        if any(c.card_id.startswith(p) for p in alias_prefixes):
            base_id = c.card_id
            for p in alias_prefixes:
                if base_id.startswith(p):
                    base_id = base_id[len(p):]
                    break
            
            # Try to find effect of base_id
            # Search in common extensions
            for ext in ["LEGACY", "EXPERT1", "CORE", "VANILLA"]:
                effect = cache.load_effect(base_id, ext)
                if effect:
                    # Found! Let's get the source code from the file
                    path = cache.get_effect_path(base_id, ext)
                    with open(path, "r") as f:
                        lines = f.readlines()
                        # Skip first line (comment) and second (empty)
                        code = "".join(lines[2:])
                        gen.implement_manually(c.card_id, code, c.card_set)
                        count += 1
                        break
                        
    print(f"Synchronized {count} alias cards (CORE, VAN, CS3) with their base effects.")

if __name__ == "__main__":
    bulk_alias_sync()
