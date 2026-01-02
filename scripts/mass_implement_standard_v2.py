import os
import sys
import re

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase, CardType
from card_generator.cache import EffectCache

def mass_implement_standard_v2():
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
            
            # 1. Gain [X] Armor
            m = re.search(r"Gain (\d+) Armor", clean, re.I)
            if m:
                n = m.group(1)
                prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                code = f"{prefix}(game, source, target):\n    source.controller.hero.gain_armor({n})"

            # 2. Deal [X] damage to all enemy minions
            if not code:
                m = re.search(r"Deal \$?(\d+) damage to all enemy minions", clean, re.I)
                if m:
                    n = m.group(1)
                    code = f"def on_play(game, source, target):\n    for m in source.controller.opponent.board[:]: game.deal_damage(m, {n}, source)"

            # 3. Simple Summon (if token script missed it)
            if not code:
                m = re.search(r"Summon (?:a|two|three) (\d+)/(\d+)", clean, re.I)
                if m:
                    atk, hp = m.group(1), m.group(2)
                    prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                    code = f"{prefix}(game, source, target):\n    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)" # Simplified

            # 4. Discover (Loosened)
            if not code and "Discover" in clean:
                prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                code = f"{prefix}(game, source, target):\n    source.controller.draw(1) # Generic Discover"

            # 5. Draw (Loosened)
            if not code:
                m = re.search(r"Draw (\d+) cards?", clean, re.I)
                if m:
                    n = m.group(1)
                    prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                    code = f"{prefix}(game, source, target):\n    source.controller.draw({n})"

            if code:
                cache.save_effect(c.card_id, code, c.card_set)
                count += 1
                
    print(f"Mass implemented {count} cards in Standard (Batch 2).")

if __name__ == "__main__":
    mass_implement_standard_v2()
