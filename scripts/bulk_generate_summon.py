import os
import sys
import re

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase, CardType
from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from scripts.token_mapper import map_tokens

def bulk_generate_summon():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    token_map = map_tokens()
    CardDatabase.get_instance().load()
    cards = CardDatabase.get_collectible_cards()
    count = 0
    
    for c in cards:
        code = None
        text = re.sub(r'<[^>]+>', '', c.text or "").replace('\n', ' ').strip()
        
        # Pattern: Summon [N] [TokenName]
        # Example: Summon two 2/2 Zombies with Taunt.
        # Example: Summon a 1/1 Imp.
        
        m = re.search(r"Summon\s*(a|an|two|three|four)?\s*(\d+/\d+)?\s*([a-zA-Z\s]+?)(?:\s*with\s*[a-zA-Z\s,]+?)?\.?$", text, re.I)
        if m:
            qty_str = m.group(1).lower() if m.group(1) else "a"
            qty = {"a": 1, "an": 1, "two": 2, "three": 3, "four": 4}.get(qty_str, 1)
            token_name = m.group(3).strip().lower()
            
            # Remove plural
            if token_name.endswith("s") and token_name[:-1] in token_map:
                token_name = token_name[:-1]
                
            token_id = token_map.get(token_name)
            if token_id:
                prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                code = f"{prefix}(game, source, target):\n"
                for i in range(qty):
                    code += f"    game.summon_token(source.controller, '{token_id}', source.zone_position + {i+1})\n"

        if code:
            gen.implement_manually(c.card_id, code, c.card_set)
            count += 1
            
    print(f"Automatically generated summon effects for {count} cards.")

if __name__ == "__main__":
    bulk_generate_summon()
