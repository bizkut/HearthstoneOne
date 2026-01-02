import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_badlands():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- SHOWDOWN IN THE BADLANDS (WW / DEEP) ---
        "WW_051": """
def on_play(game, source, target):
    for p in game.players:
        for i in range(3):
            m = create_card('WW_051t', game)
            if p == source.controller: m.rush = True
            p.summon(m)
""",
        "DEEP_017": """
def on_play(game, source, target):
    for _ in range(2):
        game.summon_token(source.controller, 'CS2_101t', source.zone_position + 1)
""",
        "DEEP_025": """
def on_play(game, source, target):
    if target:
        source.controller.add_to_hand(create_card(target.card_id, game))
        source.controller.add_to_deck(create_card(target.card_id, game))
        source.controller.summon(create_card(target.card_id, game))
""",
        "DEEP_021": """
def on_play(game, source, target):
    if target:
        source.controller.add_to_hand(create_card(target.card_id, game))
        target.destroy()
""",
        "DEEP_031": """
def on_play(game, source, target):
    if target: game.deal_damage(target, 6, source)
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.cost == 6 and c.card_type == CardType.MINION]
    if options:
        source.controller.summon(create_card(random.choice(options), game))
    source.controller.deck = source.controller.deck[:-6]
""",
        "WW_044": "def deathrattle(game, source):\n    source.controller.add_to_hand(create_card('WW_041t', game))",
        "WW_001": "def battlecry(game, source, target):\n    source.controller.draw(1)",
        "WW_042": """
def setup(game, source):
    def on_end(game, trig_src):
        if game.current_player == trig_src.controller:
            trig_src.controller.deck = trig_src.controller.deck[:-3]
    game.register_trigger('on_turn_end', source, on_end)
""",
        "DEEP_030": """
def setup(game, source):
    source.battlecry = lambda g, s, t: (s.controller.draw(1), game.deal_damage(s.controller.hero, 2, s))
    source.deathrattle = lambda g, s: (s.controller.draw(1), game.deal_damage(s.controller.hero, 2, s))
""",
        "DEEP_002": """
def on_play(game, source, target):
    import random
    cid = random.choice(['DEEP_002t', 'DEEP_002t2', 'DEEP_002t3'])
    source.controller.summon(create_card(cid, game))
""",
        "WW_024": """
def battlecry(game, source, target):
    game.summon_token(source.controller, 'WW_024t', source.zone_position + 1)
    game.summon_token(source.controller, 'WW_024t', source.zone_position + 2)
""",
        "DEEP_014": """
def setup(game, source):
    def on_atk(game, trig_src, target):
        if trig_src == source.controller.hero:
            source.controller.draw(1)
    game.register_trigger('on_attack', source, on_atk)
""", # Quick Pick
        "DEEP_016": """
def setup(game, source):
    source.lifesteal = True
    def on_dmg(game, trig_src, target, amount, dmg_src):
        if dmg_src == source.controller.hero:
            target.frozen = True
    game.register_trigger('on_damage_taken', source, on_dmg)
""", # Quartzite Crusher
        "DEEP_029": """
def on_play(game, source, target):
    # Finale condition simplified
    if source.controller.mana == 0:
        for _ in range(source.controller.mana_crystals):
            opp = source.controller.opponent.board + [source.controller.opponent.hero]
            import random
            game.deal_damage(random.choice(opp), 1, source)
""", # Trogg Gemtosser
        "ETC_026": """
def battlecry(game, source, target):
    if len(source.controller.board) == 1: # Only self
        player = source.controller
        for ctype in [CardType.SPELL, CardType.MINION, CardType.WEAPON]:
            card = next((c for c in player.deck if c.card_type == ctype), None)
            if card: player.draw_specific_card(card)
""", # Guitar Soloist
        "DEEP_034": """
def battlecry(game, source, target):
    # Condition: if played elemental last turn
    source.controller.draw(1)
""", # Shale Spider (Simplified)
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "WILD_WEST")

    print(f"Imported {len(effects)} cards for Showdown in the Badlands (WW/DEEP).")

if __name__ == "__main__":
    bulk_import_badlands()
