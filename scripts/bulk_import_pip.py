import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_pip():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- PERILS IN PARADISE (VAC) ---
        "VAC_330": "def deathrattle(game, source):\n    source.controller.add_to_hand(create_card('GAME_005', game))", # Coin
        "VAC_332": "def battlecry(game, source, target):\n    source.controller.next_other_class_cost_reduction = 2", # Sea Shill
        "VAC_335": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() 
              if c.card_type == CardType.SPELL and c.cost == 1 and c.card_class != source.controller.hero.data.card_class]
    if spells:
        for _ in range(2):
            source.controller.add_to_hand(create_card(random.choice(spells), game))
""", # Petty Theft
        "VAC_341": """
def battlecry(game, source, target):
    if target and target.attack <= source.attack:
        target.destroy()
""", # Undercooked Calamari
        "VAC_408": """
def on_play(game, source, target):
    player = source.controller
    minions = list(set([c.card_id for c in player.deck if c.card_type == CardType.MINION]))
    def on_choose(game, cid):
        card = next((c for c in game.current_player.deck if c.card_id == cid), None)
        if card: game.current_player.draw_specific_card(card)
    game.initiate_discover(player, minions, on_choose)
""", # Birdwatching
        "VAC_412": """
def battlecry(game, source, target):
    game.summon_token(source.controller.opponent, 'VAC_412t', 0)
""", # Catch of the Day
        "VAC_419": """
def on_play(game, source, target):
    for p in game.players:
        game.deal_damage(p.hero, 4, source)
""", # Acupuncture
        "VAC_427": """
def on_play(game, source, target):
    if target: game.deal_damage(target, 3, source)
""", # Corpsicle (Simplified)
        "VAC_432": "def battlecry(game, source, target):\n    source.controller.draw(1)", # Resort Valet (Simplified)
        "VAC_438": """
def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    locs = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.LOCATION]
    if locs:
        def on_choose(game, cid):
            game.current_player.add_to_hand(create_card(cid, game))
        game.initiate_discover(source.controller, random.sample(locs, min(3, len(locs))), on_choose)
""", # Travel Agent
        "VAC_337": "def setup(game, source):\n    pass", # Line Cook (Trigger on draw handled by engine eventually)
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "ISLAND_VACATION")

    print(f"Imported {len(effects)} cards for Perils in Paradise (VAC).")

if __name__ == "__main__":
    bulk_import_pip()
