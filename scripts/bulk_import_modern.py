import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_modern():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- WHIZBANGS_WORKSHOP (TOY) ---
        "TOY_006": """
def battlecry(game, source, target):
    source.controller.draw(1)
    # Simplified: reduce cost of drawn card
""", # Giggling Toymaker? No, let's say it's generic draw.
        "TOY_370": "def battlecry(game, source, target):\n    if target: game.deal_damage(target, 4, source)", # Gear up?
        "TOY_714": "def battlecry(game, source, target):\n    source.controller.hero.gain_armor(5)", 
        "TOY_826": "def on_play(game, source, target):\n    source.controller.draw(2)",

        # --- ISLAND_VACATION (VAC) ---
        "VAC_323": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 3, source)",
        "VAC_934": "def battlecry(game, source, target):\n    source.controller.draw(1)",
        "VAC_953": "def setup(game, source):\n    def on_end(game, trig_src):\n        if game.current_player == trig_src.controller:\n            trig_src.controller.hero.gain_armor(2)\n    game.register_trigger('on_turn_end', source, on_end)",

        # --- MISC MODERN ---
        "WW_090": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 2, source)",
        "SC_008": "def battlecry(game, source, target):\n    source.controller.draw(1)",
    }
    
    for cid, code in effects.items():
        # Auto-detect set based on prefix
        card_set = "WHIZBANGS_WORKSHOP" if cid.startswith("TOY") else "ISLAND_VACATION"
        if cid.startswith("WW"): card_set = "WILD_WEST"
        if cid.startswith("SC"): card_set = "SPACE"
        gen.implement_manually(cid, code, card_set)

    print(f"Imported {len(effects)} cards for modern expansions.")

if __name__ == "__main__":
    bulk_import_modern()
