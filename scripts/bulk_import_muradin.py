import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_muradin():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # Muradin, High King
        "TIME_209": """
def battlecry(game, source, target):
    player = source.controller
    # Search for High King's Hammer in deck or hand
    hammer = next((c for c in player.deck if c.card_id == 'TIME_209t'), None)
    if not hammer:
        hammer = next((c for c in player.hand if c.card_id == 'TIME_209t'), None)
    
    if hammer:
        if hammer in player.deck: player.deck.remove(hammer)
        elif hammer in player.hand: player.hand.remove(hammer)
        player.equip_weapon(hammer)
    else:
        # If not found, create a new one? (Safeguard)
        player.equip_weapon(create_card('TIME_209t', game))

def deathrattle(game, source):
    source.controller.add_to_hand(create_card('TIME_209t', game))
""",
        # High King's Hammer
        "TIME_209t": """
def setup(game, source):
    source.windfury = True

def deathrattle(game, source):
    card = create_card('TIME_209t', game)
    # Permanent buff logic would need a state tracker, simplifying to +2 Attack
    card.attack += 2
    source.controller.add_to_deck(card)
""",
        # Avatar Form
        "TIME_209t2": """
def on_play(game, source, target):
    if target:
        target.attack += 2
        # Effect: "After this attacks, deal 2 damage to all enemies"
        def on_after_attack(game, attacker, defender):
            if attacker == target:
                for enemy in game.get_opponent(attacker.controller).board + [game.get_opponent(attacker.controller).hero]:
                    game.deal_damage(enemy, 2, attacker)
        game.register_trigger('on_after_attack', target, on_after_attack)
""",
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "TIME_TRAVEL")

    print(f"Imported Muradin, High King and his relics ({len(effects)} cards).")

if __name__ == "__main__":
    bulk_import_muradin()
