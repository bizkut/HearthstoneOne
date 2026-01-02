import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_timeways_icons():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # Timelord Nozdormu
        "TIME_063": """
def setup(game, source):
    source.dormant = 5
    source.rush = True
    def on_play(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_set == 'TIME_TRAVEL':
            trig_src.dormant = max(0, trig_src.dormant - 1)
    game.register_trigger('on_card_played', source, on_play)
""",
        # Murozond, Unbounded
        "TIME_024": """
def battlecry(game, source, target):
    def on_start(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            trig_src.attack = 99 # Infinity!
    game.register_trigger('on_turn_start', source, on_start)
""",
        # Chromie
        "TIME_103": """
def deathrattle(game, source):
    # Draw copies of cards played this game
    played = [c for c in source.controller.cards_played_this_game]
    for cid in played[:3]: # Draw up to 3 for balance
         source.controller.add_to_hand(create_card(cid, game))
""",
        # Lady Azshara
        "TIME_211": """
def on_play(game, source, target):
    # Simplified Choose One
    import random
    if random.random() > 0.5:
        # Empower Zin-Azshari (Buff all board?)
        for m in source.controller.board: m.attack += 2; m.health += 2
    else:
        # Well of Eternity (Restore mana/health?)
        source.controller.mana = source.controller.max_mana
""",
        # Medivh the Hallowed
        "TIME_890": """
def battlecry(game, source, target):
    for m in game.current_player.board[:] + game.current_player.opponent.board[:]:
        if m != source:
            m.silence()
            m.destroy()
""",
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "TIME_TRAVEL")

    print(f"Imported additional Timeways Icons ({len(effects)} cards).")

if __name__ == "__main__":
    bulk_import_timeways_icons()
