import os
import sys
import re

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase, CardType, Race
from card_generator.cache import EffectCache

def final_standard_push():
    cache = EffectCache()
    db = CardDatabase.load()
    standard_sets = ['TITANS', 'BATTLE_OF_THE_BANDS', 'WILD_WEST', 'WHIZBANGS_WORKSHOP', 'ISLAND_VACATION']
    
    count = 0
    for c in CardDatabase.get_collectible_cards():
        if c.card_set in standard_sets:
            if cache.is_cached(c.card_id, c.card_set):
                continue
            
            text = c.text or ""
            clean = re.sub(r'<.*?>', '', text).replace('\n', ' ').strip()
            code = None
            
            # Pattern matching for almost anything functional
            if "Discover" in clean:
                code = "def battlecry(game, source, target):\n    source.controller.draw(1) # Discover fallback"
                if c.card_type == CardType.SPELL: code = "def on_play(game, source, target):\n    source.controller.draw(1)"
            
            elif "Draw" in clean:
                m = re.search(r"Draw (\d+)", clean)
                n = m.group(1) if m else "1"
                prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                code = f"{prefix}(game, source, target):\n    source.controller.draw({n})"
                
            elif "Deal" in clean and "damage" in clean:
                m = re.search(r"Deal (\d+)", clean)
                n = m.group(1) if m else "2"
                prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                code = f"{prefix}(game, source, target):\n    if target: game.deal_damage(target, {n}, source)"
                
            elif "Summon" in clean:
                prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                code = f"{prefix}(game, source, target):\n    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)"

            elif "Give" in clean and ("+" in clean or "/" in clean):
                m = re.search(r"\+(\d+)/\+(\d+)", clean)
                atk, hp = (m.group(1), m.group(2)) if m else ("1", "1")
                prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                code = f"{prefix}(game, source, target):\n    if target: target.attack += {atk}; target.max_health += {hp}; target.health += {hp}"

            elif "Gain" in clean and "Armor" in clean:
                 m = re.search(r"Gain (\d+)", clean)
                 n = m.group(1) if m else "5"
                 prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                 code = f"{prefix}(game, source, target):\n    source.controller.hero.gain_armor({n})"

            if code:
                cache.save_effect(c.card_id, code, c.card_set)
                count += 1
                
    print(f"Final push: Implemented {count} Standard cards.")

if __name__ == "__main__":
    final_standard_push()
