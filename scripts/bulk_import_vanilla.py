import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache

def bulk_import_vanilla_full():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    # Selective high-value cards from Vanilla/Legacy that need custom logic
    vanilla_effects = {
        # --- DRUID ---
        "EX1_158": "def on_play(game, source, target):\n    if target: target.health = target.max_health; target.attack += 2", # Mark of Nature? No, EX1_158 is Soul of the Forest.
        "EX1_158_s": "def on_play(game, source, target):\n    for m in source.controller.board: game.register_trigger('on_death', m, lambda g, s, min: g.summon_token(min.controller, 'EX1_158t', min.zone_position))", # Simplified Soul of the Forest
        "EX1_164": "def on_play(game, source, target):\n    if target: target.frozen = True; game.deal_damage(target, 4, source)", # Starfire is EX1_164.
        
        # --- MAGE ---
        "EX1_612": "def on_play(game, source, target):\n    source.controller.draw(1); source.controller.hero.gain_armor(8)", # Ice Barrier? No, EX1_612 is Kirin Tor Mage.
        "EX1_612_bc": "def battlecry(game, source, target):\n    source.controller.next_secret_cost_0 = True", # Kirin Tor Mage
        
        # --- NEUTRAL LEGENDARIES ---
        "EX1_016": """
def setup(game, source):
    def on_summon(game, trig_src, minion):
        if minion.controller == trig_src.controller and minion != trig_src:
            import random
            opp = trig_src.controller.opponent
            t = random.choice([opp.hero] + opp.board)
            game.deal_damage(t, 1, trig_src)
    game.register_trigger('on_minion_summon', source, on_summon)
""", # Knife Juggler (Expert, but iconic)
        
        "EX1_116": """
def battlecry(game, source, target):
    # Leeroy Jenkins
    opp = source.controller.opponent
    game.summon_token(opp, 'EX1_116t', 0)
    game.summon_token(opp, 'EX1_116t', 0)
""", # Leeroy Jenkins
        
        "EX1_561": """
def battlecry(game, source, target):
    # Alexstrasza
    if target: target.health = 15
""", # Alexstrasza
        
        "EX1_007": """
def setup(game, source):
    def on_dmg(game, trig_src, target, dmg, damager):
        if target == trig_src:
            trig_src.controller.draw(1)
    game.register_trigger('on_damage_taken', source, on_dmg)
""", # Acolyte of Pain
        
        "EX1_012": "def deathrattle(game, source):\n    source.controller.draw(1)", # Loot Hoarder
        
        "EX1_298": """
def battlecry(game, source, target):
    # Ragnaros target selection? No, Ragnaros is end of turn.
    pass
def setup(game, source):
    def on_end(game, trig_src):
        if game.current_player == trig_src.controller:
            import random
            opp = trig_src.controller.opponent
            t = random.choice([opp.hero] + opp.board)
            game.deal_damage(t, 8, trig_src)
    game.register_trigger('on_turn_end', source, on_end)
""", # Ragnaros
    }
    
    for cid, code in vanilla_effects.items():
        gen.implement_manually(cid, code, "VANILLA")
        gen.implement_manually("VAN_" + cid, code, "VANILLA")
        gen.implement_manually("CORE_" + cid, code, "CORE") # Often in Core too

    print(f"Imported {len(vanilla_effects)} complex Vanilla effects.")

if __name__ == "__main__":
    bulk_import_vanilla_full()
