import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_standard_iconic():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        "TTN_960": """
def battlecry(game, source, target):
    # Sargeras: Open portal
    game.summon_token(source.controller, 'TTN_960t', 0) # Portal
""", # Sargeras
        "WW_0700": """
def battlecry(game, source, target):
    p = source.controller
    ids = [c.card_id for c in p.deck]
    if len(ids) == len(set(ids)):
        for m in p.opponent.board[:]:
            m.destroy() # Poof!
""", # Reno, Lone Ranger
        "CORE_LOE_011": """
def battlecry(game, source, target):
    p = source.controller
    ids = [c.card_id for c in p.deck]
    if len(ids) == len(set(ids)):
        p.hero.health = p.hero.max_health
""", # Reno Jackson
        "ETC_085": """
def on_play(game, source, target):
    # Symphony of Sins: Discover movement
    source.controller.draw(1) # Simplified
""", # Symphony of Sins
        "ETC_087": """
def battlecry(game, source, target):
    source.controller.max_hand_size = 11
    # Simplified: no max mana 11 yet
""", # Audio Amplifier
        "ETC_324": """
def setup(game, source):
    source.divine_shield = True
    def on_lose_ds(game, trig_src, target):
        if target.controller == source.controller:
            source.controller.draw(1)
    # Note: needs 'on_lose_divine_shield' event in engine
    game.register_trigger('on_damage_taken', source, lambda g, s, t, a, src: on_lose_ds(g, s, t))
""", # Jitterbug
        "ETC_318": """
def on_play(game, source, target):
     p = source.controller
     count = 2
     if p.mana == 0: count = 3
     for _ in range(count):
         c = next((x for x in p.deck if x.cost == 1), None)
         if c: p.draw_specific_card(c); p.summon(c)
""", # Boogie Down
        "ETC_205": """
def on_play(game, source, target):
    source.controller.draw(3)
""", # Volume Up
        "ETC_206": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL]
    if spells: source.controller.add_to_hand(create_card(random.choice(spells), game))
    if source.controller.mana == 0:
         # Simplified: hand back for finale
         pass
""", # Infinitize the Maxitude
    }
    
    for cid, code in effects.items():
        # Auto-set detection
        if cid.startswith("TTN"): s = "TITANS"
        elif cid.startswith("WW") or cid.startswith("DEEP"): s = "WILD_WEST"
        elif cid.startswith("ETC") or cid.startswith("JAM"): s = "BATTLE_OF_THE_BANDS"
        elif cid.startswith("CORE"): s = "CORE"
        else: s = "LEGACY"
        gen.implement_manually(cid, code, s)

    print(f"Imported {len(effects)} iconic Standard cards.")

if __name__ == "__main__":
    bulk_import_standard_iconic()
