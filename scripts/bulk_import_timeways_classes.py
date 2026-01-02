import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_timeways_classes():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # Warrior: Lo'Gosh, Blood Fighter
        "TIME_850": """
def deathrattle(game, source):
    # Summon Blood Fighter from hand (simplified: summon a 5/5 copy)
    p = source.controller
    target = next((c for c in p.hand if 'Blood Fighter' in c.name), None)
    if not target:
        target = create_card('TIME_850', game) # Self-copy
    p.summon(target)
    target.attack += 5; target.max_health += 5; target.health += 5
    # Force attack random enemy
    opp = game.get_opponent(p).board + [game.get_opponent(p).hero]
    import random
    if opp: game.deal_damage(random.choice(opp), target.attack, target)
""",
        # Hunter: Ranger General Sylvanas
        "TIME_609": """
def battlecry(game, source, target):
    # Deal 2 damage to all enemies, repeat logic simplified
    repeats = 1
    # Check for sisters in history
    played = [c.name for c in source.controller.cards_played_this_game]
    if 'Alleria' in played: repeats += 1
    if 'Vereesa' in played: repeats += 1
    for _ in range(repeats):
        for m in game.get_opponent(source.controller).board[:] + [game.get_opponent(source.controller).hero]:
            game.deal_damage(m, 2, source)
""",
        # Mage: Timelooper Toki
        "TIME_861": """
def battlecry(game, source, target):
    # Get 3 random spells from the past
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL and c.card_set != 'TIME_TRAVEL']
    for _ in range(3):
        source.controller.add_to_hand(create_card(random.choice(options), game))
""",
        # Paladin: Gelbin of Tomorrow
        "TIME_009": """
def battlecry(game, source, target):
    # Put aura from deck to battlefield - simplified: draw 2 spells
    source.controller.draw(2)
""",
        # Priest: Eternus
        "TIME_435": """
def battlecry(game, source, target):
    if target and target.health <= source.health:
        # Steal minion
        target.controller.board.remove(target)
        source.controller.board.append(target)
        target.controller = source.controller
""",
        # Rogue: Garona Halforcen
        "TIME_875": """
def battlecry(game, source, target):
    opp = source.controller.opponent
    # Kill Llane placeholder
    opp.hero.health //= 2
""",
        # Shaman: Stormrook
        "TIME_217": """
def setup(game, source):
    def on_dmg(game, trig_src, target, amount, dmg_src):
        if target == trig_src and getattr(dmg_src, 'spell_school', None) == 'NATURE':
            # Summon 5-cost instead of damage (simplified fix)
            source.controller.summon(create_card('CS2_182', game)) # Boulderfist Ogre placeholder
    game.register_trigger('on_damage_taken', source, on_dmg)
""",
        # Warlock: Bygone Doomspeaker
        "TIME_008": """
def battlecry(game, source, target):
    source.controller.discard(1)
    source.controller.opponent.discard(1)
    # Rewind placeholder
    source.controller.draw(1)
""",
        # Druid: Krona, Keeper of Eons
        "TIME_705": """
def battlecry(game, source, target):
    # Set bottom 5 costs to 1
    for c in source.controller.deck[-5:]:
        c.cost = 1
""",
        # DK: Broxigar
        "TIME_020": """
def setup(game, source):
    source.charge = True
""",
        # DH: Chrono-Lord Epoch
        "TIME_714": """
def battlecry(game, source, target):
    # Destroy minions played last turn
    history = source.controller.opponent.cards_played_last_turn
    for m in source.controller.opponent.board[:]:
        if m.card_id in history:
            m.destroy()
""",
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "TIME_TRAVEL")

    print(f"Imported Timeways Class Icons ({len(effects)} cards).")

if __name__ == "__main__":
    bulk_import_timeways_classes()
