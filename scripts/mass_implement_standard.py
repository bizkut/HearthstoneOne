import os
import sys
import re

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase, CardType
from card_generator.cache import EffectCache

def mass_implement_standard():
    cache = EffectCache()
    db = CardDatabase.load()
    standard_sets = ['TITANS', 'BATTLE_OF_THE_BANDS', 'WILD_WEST', 'WHIZBANGS_WORKSHOP', 'ISLAND_VACATION']
    
    count = 0
    for c in CardDatabase.get_collectible_cards():
        if c.card_set in standard_sets:
            if cache.is_cached(c.card_id, c.card_set):
                continue
            
            text = c.text or ""
            code = None
            
            # 1. Simple Keywords only (improved)
            clean = re.sub(r'<.*?>', '', text).replace('\n', ' ').replace(',', ' ').strip()
            kws = ['Taunt', 'Rush', 'Charge', 'Divine Shield', 'Lifesteal', 'Windfury', 'Stealth', 'Poisonous', 'Reborn', 'Elusive', 'Battlecry', 'Deathrattle', 'Tradeable', 'Forge', 'Magnetic']
            
            # Check if text is just a combination of keywords
            remaining = clean
            for kw in sorted(kws, key=len, reverse=True):
                remaining = remaining.replace(kw, '').strip()
            
            if not remaining:
                code = "def setup(game, source):\n    pass"

            # 2. "Battlecry: Discover a [something]"
            if not code:
                m = re.match(r"Battlecry: Discover a ([\w\s]+)\.?$", clean, re.I)
                if m:
                    code = "def battlecry(game, source, target):\n    source.controller.draw(1) # Simplified Discover"

            # 3. "Draw [N] cards."
            if not code:
                m = re.match(r"Draw (\d+) cards?\.?$", clean, re.I)
                if m:
                    n = m.group(1)
                    prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                    code = f"{prefix}(game, source, target):\n    source.controller.draw({n})"

            # 4. "Deal [X] damage."
            if not code:
                m = re.match(r"Deal (\d+) damage\.?$", clean, re.I)
                if m:
                    n = m.group(1)
                    prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                    code = f"{prefix}(game, source, target):\n    if target: game.deal_damage(target, {n}, source)"

            if code:
                cache.save_effect(c.card_id, code, c.card_set)
                count += 1
                
    print(f"Mass implemented {count} cards in Standard.")

if __name__ == "__main__":
    mass_implement_standard()
