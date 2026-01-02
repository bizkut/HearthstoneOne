import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_standard_final_1():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- DEEP SET (Badlands Mini-set) ---
        "DEEP_003": """
def on_play(game, source, target):
    if target: 
        game.deal_damage(target, 1, source)
        from simulator.card_loader import CardDatabase
        import random
        # Summon random minion of that cost (1)
        options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.cost == 1 and c.card_type == CardType.MINION]
        if options: source.controller.summon(create_card(random.choice(options), game))
""", # Shimmer Shot
        "DEEP_012": """
def battlecry(game, source, target):
    if source.controller.hero.weapon:
        w = source.controller.hero.weapon
        source.attack += w.attack
        source.max_health += w.durability
        source.health += w.durability
        # Simplified: doesn't "give it back" yet
""", # Shadestone Skulker
        "DEEP_014": """
def setup(game, source):
    def on_atk(game, trig_src, target):
        if trig_src == source.controller.hero:
            source.controller.draw(1)
    game.register_trigger('on_attack', source, on_atk)
""", # Quick Pick
        "DEEP_018": """
def on_play(game, source, target):
    if target: target.divine_shield = True
    source.controller.draw(1) # Simplified Excavate
""", # Shroomscavate
        "DEEP_019": """
def on_play(game, source, target):
    if target:
        copy = create_card(target.card_id, game)
        # Simplified: doesn't go dormant, just summons
        source.controller.summon(copy)
""", # Crimson Expanse
        "DEEP_026": """
def on_play(game, source, target):
    player = source.controller
    minions = [c.card_id for c in player.deck if c.card_type == CardType.MINION]
    if minions:
        import random
        chosen = random.sample(minions, min(3, len(minions)))
        def on_choose(game, cid):
            card = next((c for c in game.current_player.deck if c.card_id == cid), None)
            if card:
                game.current_player.draw_specific_card(card)
                game.current_player.hero.health += card.cost
        game.initiate_discover(player, chosen, on_choose)
""", # Pendant of Earth

        # --- ISLAND VACATION (VAC) ---
        "VAC_305": """
def on_play(game, source, target):
    game.summon_token(source.controller, 'VAC_305t', 0)
    game.summon_token(source.controller, 'VAC_305t', 0)
""", # Frosty Decor
        "VAC_327": "def battlecry(game, source, target):\n    if target: target.attack += 3; target.max_health += 3; target.health += 3; target.frozen = True", # Cryopractor
        "VAC_333": """
def battlecry(game, source, target):
    # Replay last card from another class
    history = [c for c in source.controller.cards_played_this_game if c.card_class != source.controller.hero.data.card_class]
    if history:
        game.play_card(create_card(history[-1], game))
""", # Conniving Conman
        "VAC_404": """
def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)
    game.deal_damage(source.controller.hero, 2, source)
""", # Nightshade Tea
        "VAC_416": """
def on_play(game, source, target):
    if target:
        atk = target.attack
        target.destroy()
        for _ in range(atk):
            opp = source.controller.opponent.board + [source.controller.opponent.hero]
            import random
            game.deal_damage(random.choice(opp), 1, source)
""", # Death Roll
        "VAC_304": """
def battlecry(game, source, target):
    # Discovery of cast spells while holding - simplified to just last 3 spells
    options = source.controller.spells_played_this_game[-3:]
    if options:
        def on_choose(game, cid):
            game.current_player.add_to_hand(create_card(cid, game))
        game.initiate_discover(source.controller, options, on_choose)
""", # Tidepool Pupil
    }
    
    for cid, code in effects.items():
        # Auto-detect set based on prefix
        card_set = "WILD_WEST" if cid.startswith("DEEP") else "ISLAND_VACATION"
        gen.implement_manually(cid, code, card_set)

    print(f"Imported {len(effects)} Standard cards (Batch 1).")

if __name__ == "__main__":
    bulk_import_standard_final_1()
