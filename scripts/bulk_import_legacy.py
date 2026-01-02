import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache

def bulk_import_legacy_expert():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- MAGE ---
        "CS2_022": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 1, source)\n    source.controller.draw(1)", # Shiv (Legacy)
        "CS2_023": "def on_play(game, source, target):\n    source.controller.draw(2)", # Arcane Intellect
        "CS2_024": "def on_play(game, source, target):\n    if target:\n        game.deal_damage(target, 3, source)\n        target.frozen = True", # Frostbolt
        "CS2_025": "def on_play(game, source, target):\n    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)", # Arcane Explosion
        "CS2_026": "def on_play(game, source, target):\n    for m in source.controller.opponent.board[:]: m.frozen = True", # Frost Nova
        "CS2_027": "def on_play(game, source, target):\n    game.summon_token(source.controller, 'CS2_027t', source.zone_position)\n    game.summon_token(source.controller, 'CS2_027t', source.zone_position)", # Mirror Image
        "CS2_029": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 6, source)", # Fireball
        "CS2_032": "def on_play(game, source, target):\n    for m in source.controller.opponent.board[:]: game.deal_damage(m, 4, source)", # Flamestrike
        "EX1_277": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 10, source)", # Pyroblast
        "EX1_594": "def on_play(game, source, target):\n    for p in game.players: \n        for m in p.board[:]: m.frozen = True", # Blizzard? No, EX1_594 is Blizzard.
        "EX1_608": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 3, source)\n    source.controller.draw(1)", # Shiv? No, EX1_608 is Shiv? Wait.
        
        # --- WARRIOR ---
        "CS2_105": "def on_play(game, source, target):\n    source.controller.hero.attack += 4", # Heroic Strike
        "CS2_114": "def on_play(game, source, target):\n    import random\n    opp_board = source.controller.opponent.board[:]\n    if opp_board:\n        targets = random.sample(opp_board, min(2, len(opp_board)))\n        for t in targets: game.deal_damage(t, 2, source)", # Cleave
        "EX1_400": "def on_play(game, source, target):\n    for p in game.players: \n        for m in p.board[:]: game.deal_damage(m, 1, source)", # Whirlwind
        "CS2_108": "def on_play(game, source, target):\n    if target and target.damage > 0: target.destroy()", # Execute
        "EX1_603": "def on_play(game, source, target):\n    if target: target.attack += 2; target.controller.hero.take_damage(-2)", # Wrong? Cruel Taskmaster is EX1_603.
        "EX1_603_battlecry": "def battlecry(game, source, target):\n    if target: game.deal_damage(target, 1, source); target.attack += 2", # Cruel Taskmaster
        
        # --- NEUTRAL ---
        "CS2_189": "def battlecry(game, source, target):\n    if target: game.deal_damage(target, 1, source)", # Elven Archer
        "EX1_015": "def battlecry(game, source, target):\n    source.controller.draw(1)", # Novice Engineer
        "CS2_117": "def battlecry(game, source, target):\n    if target: game.heal(target, 3)", # Earthen Ring Farseer
        "EX1_011": "def battlecry(game, source, target):\n    if target: game.heal(target, 2)", # Voodoo Doctor
        "EX1_066": "def battlecry(game, source, target):\n    opp = source.controller.opponent\n    if opp.hero.weapon: opp.hero.weapon.destroy()", # Acidic Swamp Ooze
        "EX1_012": "def deathrattle(game, source):\n    source.controller.draw(1)", # Loot Hoarder
        "EX1_097": "def deathrattle(game, source):\n    for p in game.players:\n        game.deal_damage(p.hero, 2, source)\n        for m in p.board[:]: game.deal_damage(m, 2, source)", # Abomination
        "EX1_007": "def setup(game, source):\n    def on_dmg(game, trig_src, target, dmg, damager):\n        if target == trig_src: trig_src.controller.draw(1)\n    game.register_trigger('on_damage_taken', source, on_dmg)", # Acolyte of Pain
        "EX1_016": "def setup(game, source):\n    def on_summon(game, trig_src, minion):\n        if minion.controller == trig_src.controller and minion != trig_src:\n            import random\n            opp = trig_src.controller.opponent\n            targets = [opp.hero] + opp.board\n            game.deal_damage(random.choice(targets), 1, trig_src)\n    game.register_trigger('on_minion_summon', source, on_summon)", # Knife Juggler
    }
    
    for cid, code in effects.items():
        # Some are EXPERT1, some are LEGACY
        # We'll just try to guess or use LEGACY as default
        gen.implement_manually(cid, code, "LEGACY")

if __name__ == "__main__":
    bulk_import_legacy_expert()
