import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_toy():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- WHIZBANGS_WORKSHOP (TOY / MIS) ---
        "MIS_703": "def battlecry(game, source, target):\n    source.controller.hero.health = 15", # INFERNAL!
        "MIS_301": """
def on_play(game, source, target):
    game.summon_token(source.controller, 'EX1_158t', source.zone_position + 1)
    treants = [m for m in source.controller.board if 'Treant' in m.name]
    source.controller.draw(len(treants))
""", # Overgrown Beanstalk
        "MIS_302": """
def on_play(game, source, target):
    if target:
        target.frozen = True
        copy = create_card(target.card_id, game)
        if source.controller.summon(copy):
            copy.frozen = True
""", # Buy One, Get One Freeze
        "MIS_307": """
def battlecry(game, source, target):
    tinyfin = create_card('CS2_168', game)
    tinyfin.attack = source.attack
    tinyfin.max_health = source.health
    tinyfin.health = source.health
    tinyfin.rush = True
    source.controller.summon(tinyfin, source.zone_position + 1)
""", # Murloc Growfin
        "TOY_046": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.cost == 4 and c.card_type == CardType.MINION]
    if options:
        def on_choose(game, cid):
            card = create_card(cid, game)
            card.attack = 7; card.max_health = 7; card.health = 7
            game.current_player.add_to_hand(card)
        game.initiate_discover(source.controller, random.sample(options, min(3, len(options))), on_choose)
""", # Incredible Value
        "TOY_037": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    secrets = [c.card_id for c in CardDatabase.get_collectible_cards() if 'Secret:' in (c.text or "")]
    if secrets:
        def on_choose(game, cid):
            card = create_card(cid, game)
            card.cost = 1
            game.current_player.add_to_hand(card)
        game.initiate_discover(source.controller, random.sample(secrets, min(3, len(secrets))), on_choose)
""", # Hidden Objects
        "MIS_705": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    taunts = [c.card_id for c in CardDatabase.get_collectible_cards() if c.taunt]
    if taunts:
        for _ in range(5):
             source.controller.add_to_hand(create_card(random.choice(taunts), game))
""", # Standardized Pack
        "MIS_707": """
def on_play(game, source, target):
    source.controller.draw(2)
    game.deal_damage(source.controller.hero, 3, source)
    source.controller.add_to_deck(create_card('MIS_707', game))
    source.controller.add_to_deck(create_card('MIS_707', game))
""", # Mass Production
        "MIS_708": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    others = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_class != source.controller.hero.data.card_class]
    if others:
        for _ in range(5):
             source.controller.add_to_hand(create_card(random.choice(others), game))
""", # Twisted Pack
        "MIS_714": """
def on_play(game, source, target):
    if target:
        copy = create_card(target.card_id, game)
        if source.controller.summon(copy):
             game.attack(copy, target)
""", # Funhouse Mirror
        "MIS_107": """
def on_play(game, source, target):
    dmg = 3
    if not any(c.card_type == CardType.MINION for c in source.controller.deck):
        dmg = 6
    for _ in range(dmg):
        opp = source.controller.opponent.board[:]
        if opp:
            import random
            game.deal_damage(random.choice(opp), 1, source)
""", # Malfunction
        "MIS_104": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    beasts = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.BEAST]
    if beasts:
        for _ in range(5):
             source.controller.add_to_hand(create_card(random.choice(beasts), game))
""", # Wilderness Pack
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "WHIZBANGS_WORKSHOP")

    print(f"Imported {len(effects)} cards for Whizbang's Workshop (TOY/MIS).")

if __name__ == "__main__":
    bulk_import_toy()
