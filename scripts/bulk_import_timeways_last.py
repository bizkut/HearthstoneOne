import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_timeways_last_two():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # The Eternal Hold: Discover Demon (5+). If no minions in deck, next costs (0).
        "TIME_446": """
def on_play(game, source, target):
    p = source.controller
    import random
    from simulator.card_loader import CardDatabase
    demons = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.DEMON and c.cost >= 5]
    if demons:
        # Simplified Discover: add random to hand
        p.add_to_hand(create_card(random.choice(demons), game))
    
    # Deck check
    has_minion = any(c.card_type == CardType.MINION for c in p.deck)
    if not has_minion:
        # Next demon costs 0 logic placeholder
        pass
""",
        # Husk, Eternal Reaper: Deathrattle resurrect with Health = Corpses spent
        "TIME_618": """
def battlecry(game, source, target):
    p = source.controller
    # Death Knight mechanic: spend corpses to resurrect hero
    def on_hero_death(game, hero):
        if hero.controller == p and getattr(p, 'corpses', 0) > 0:
            spent = min(20, p.corpses)
            p.corpses -= spent
            hero.health = spent
            # Cancel death logic would be needed in engine, simplified fix:
            return True # Cancel death
    game.register_trigger('on_hero_death', source, on_hero_death)
""",
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "TIME_TRAVEL")

    print(f"Imported the last 2 legends of Across the Timeways ({len(effects)} cards).")

if __name__ == "__main__":
    bulk_import_timeways_last_two()
