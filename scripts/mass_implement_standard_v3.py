import os
import sys
import re

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase, CardType
from card_generator.cache import EffectCache

def mass_implement_standard_v3():
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
            
            # 1. Give a minion +X/+Y
            m = re.search(r"Give (?:a|all) friendly minions? \+(\d+)/\+(\d+)", clean, re.I)
            if m:
                atk, hp = m.group(1), m.group(2)
                prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                code = f"{prefix}(game, source, target):\n    if target:\n        target.attack += {atk}; target.max_health += {hp}; target.health += {hp}"
                if "all" in m.group(0).lower():
                    code = f"{prefix}(game, source, target):\n    for m in source.controller.board: m.attack += {atk}; m.max_health += {hp}; m.health += {hp}"

            # 2. Give a minion [Keyword]
            if not code:
                m = re.search(r"Give a minion (Taunt|Rush|Charge|Divine Shield|Lifesteal|Windfury|Stealth|Poisonous|Reborn)", clean, re.I)
                if m:
                    kw = m.group(1).lower().replace(' ', '_')
                    prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                    code = f"{prefix}(game, source, target):\n    if target: setattr(target, '{kw}', True)"

            # 3. Destroy an enemy minion
            if not code and "Destroy an enemy minion" in clean:
                prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                code = f"{prefix}(game, source, target):\n    if target: target.destroy()"

            # 4. Give your weapon +X Attack/Durability
            if not code:
                m = re.search(r"Give your weapon \+(\d+) (Attack|Durability)", clean, re.I)
                if m:
                    n, attr = m.group(1), m.group(2).lower()
                    prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                    code = f"{prefix}(game, source, target):\n    if source.controller.hero.weapon: source.controller.hero.weapon.{attr} += {n}"

            # 5. Costs (1) less / (1) more
            if not code and "Costs (1) less" in clean:
                code = "def setup(game, source):\n    pass # Managed by hand aura"

            if code:
                cache.save_effect(c.card_id, code, c.card_set)
                count += 1
                
    print(f"Mass implemented {count} cards in Standard (Batch 3).")

if __name__ == "__main__":
    mass_implement_standard_v3()
