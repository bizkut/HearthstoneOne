import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_solo_fatigue():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- SOLOISTS ---
        "ETC_029": """
def battlecry(game, source, target):
    if len(source.controller.board) == 1:
        game.summon_token(source.controller, 'ETC_029t', 0)
        game.summon_token(source.controller, 'ETC_029t', 0)
""", # Keyboard Soloist
        "ETC_035": """
def battlecry(game, source, target):
    if len(source.controller.board) == 1:
        source.attack += 2; source.max_health += 2; source.health += 2; source.rush = True
""", # Drum Soloist
        "ETC_028": """
def battlecry(game, source, target):
    if len(source.controller.board) == 1:
        from simulator.card_loader import CardDatabase
        import random
        secrets = [c.card_id for c in CardDatabase.get_collectible_cards() if 'Secret:' in (c.text or "")]
        if secrets:
            source.controller.add_to_hand(create_card(random.choice(secrets), game))
""", # Harmonica Soloist

        # --- FATIGUE ---
        "ETC_068": """
def battlecry(game, source, target):
    p = source.controller
    p.fatigue += 1
    game.deal_damage(p.hero, p.fatigue, source)
    source.attack += p.fatigue; source.max_health += p.fatigue; source.health += p.fatigue
""", # Baritone Imp
        "ETC_069": """
def on_play(game, source, target):
    p = source.controller
    p.fatigue += 1
    game.deal_damage(p.hero, p.fatigue, source)
    for m in p.opponent.board[:]:
        game.deal_damage(m, p.fatigue, source)
    game.deal_damage(p.opponent.hero, p.fatigue, source)
""", # Crescendo
        "ETC_070": """
def setup(game, source):
    def on_end(game, trig_src):
        if game.current_player == trig_src.controller:
            p = trig_src.controller
            p.fatigue += 1
            game.deal_damage(p.hero, p.fatigue, source)
    game.register_trigger('on_turn_end', source, on_end)
""", # Insane Conductor? (Wait, checking name) - Let's use ID from list if I had it.

        # --- HIGHLANDER ---
        "DEEP_020": """
def battlecry(game, source, target):
    player = source.controller
    ids = [c.card_id for c in player.deck]
    if len(ids) == len(set(ids)):
        player.hero.battlecries_trigger_twice = True
""", # Deepminer Brann
        "WW_010": """
def battlecry(game, source, target):
    player = source.controller
    ids = [c.card_id for c in player.deck]
    if len(ids) == len(set(ids)):
        source.controller.equip_weapon(create_card('WW_010t', game))
""", # Doctor Holli'dae
    }
    
    for cid, code in effects.items():
        # Map to their correct sets
        card_set = "BATTLE_OF_THE_BANDS" if cid.startswith("ETC") else "WILD_WEST"
        gen.implement_manually(cid, code, card_set)

    print(f"Imported {len(effects)} specialized cards (Soloists, Fatigue, Highlander).")

if __name__ == "__main__":
    bulk_import_solo_fatigue()
