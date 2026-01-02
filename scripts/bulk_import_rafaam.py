import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_rafaam():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    rafaam_ids = [
        'TIME_005', 'TIME_005t1', 'TIME_005t2', 'TIME_005t3', 
        'TIME_005t4', 'TIME_005t5', 'TIME_005t6', 
        'TIME_005t7', 'TIME_005t8', 'TIME_005t9'
    ]
    
    effects = {
        # Timethief Rafaam (Main)
        "TIME_005": """
def battlecry(game, source, target):
    player = source.controller
    # Track played Rafaams
    played = getattr(player, 'rafaams_played', set())
    # The 'rest' means the 9 others
    others = {
        'TIME_005t1', 'TIME_005t2', 'TIME_005t3', 
        'TIME_005t4', 'TIME_005t5', 'TIME_005t6', 
        'TIME_005t7', 'TIME_005t8', 'TIME_005t9'
    }
    print(f"DEBUG: Played count = {len(played)}")
    print(f"DEBUG: Missing = {others - played}")
    if others.issubset(played):
        print("DEBUG: EXODIA CONDITION MET!")
        game.deal_damage(player.opponent.hero, 100, source) # Exodia!
    else:
        print("DEBUG: EXODIA CONDITION NOT MET.")

def setup(game, source):
    # Register that a Rafaam was played
    def on_play(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_id.startswith('TIME_005'):
             played = getattr(trig_src.controller, 'rafaams_played', set())
             played.add(card.card_id)
             trig_src.controller.rafaams_played = played
    game.register_trigger('on_card_played', source, on_play)
""",
        # Tiny Rafaam
        "TIME_005t1": """
def battlecry(game, source, target):
    # Draw a Rafaam
    player = source.controller
    c = next((x for x in player.deck if x.card_id.startswith('TIME_005')), None)
    if c: player.draw_specific_card(c)

def deathrattle(game, source):
    # Draw a Rafaam
    player = source.controller
    c = next((x for x in player.deck if x.card_id.startswith('TIME_005')), None)
    if c: player.draw_specific_card(c)
""",
        # Green Rafaam
        "TIME_005t2": """
def battlecry(game, source, target):
    player = source.controller
    for c in player.hand:
        if c.card_id.startswith('TIME_005'):
            c.attack += 2; c.max_health += 2; c.health += 2
    for m in player.board:
        if m.card_id.startswith('TIME_005'):
            m.attack += 2; m.max_health += 2; m.health += 2
""",
        # Explorer Rafaam
        "TIME_005t3": """
def battlecry(game, source, target):
    player = source.controller
    rafaams = [c.card_id for c in player.deck if c.card_id.startswith('TIME_005')]
    if rafaams:
        def on_choose(game, cid):
            card = next((c for c in game.current_player.deck if c.card_id == cid), None)
            if card: game.current_player.draw_specific_card(card)
        game.initiate_discover(player, rafaams[:3], on_choose)
""",
        # Warchief Rafaam
        "TIME_005t4": """
def battlecry(game, source, target):
    p = source.controller
    armor = 5
    if any(c.card_id.startswith('TIME_005') for c in p.hand if c != source):
        armor += 5
    p.hero.gain_armor(armor)
""",
        # Mindflayer R'faam
        "TIME_005t5": """
def battlecry(game, source, target):
    p = source.controller
    if any(c.card_id.startswith('TIME_005') for c in p.hand if c != source):
        p.summon(create_card(source.card_id, game))
""",
        # Calamitous Rafaam
        "TIME_005t6": """
def battlecry(game, source, target):
    for m in game.current_player.board[:] + game.current_player.opponent.board[:]:
        if not m.card_id.startswith('TIME_005'):
            game.deal_damage(m, 6, source)
""",
        # Giant Rafaam
        "TIME_005t7": """
def setup(game, source):
     # Rush is keyword
     pass
""", # Cost reduction in hand would need hand_aura
        # Murloc Rafaam
        "TIME_005t8": """
def battlecry(game, source, target):
    # Next Rafaam costs 3 less
    pass
""",
        # Archmage Rafaam
        "TIME_005t9": """
def battlecry(game, source, target):
    for m in game.current_player.board[:] + game.current_player.opponent.board[:]:
        if not m.card_id.startswith('TIME_005'):
            m.transform('CS2_168') # Sheep
""",
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "TIME_TRAVEL")

    print(f"Imported Rafaam, Time Thief and his gang ({len(effects)} cards).")

if __name__ == "__main__":
    bulk_import_rafaam()
