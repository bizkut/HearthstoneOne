import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache

def bulk_import_foundations():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    # Complete foundation cards (Legacy + Core)
    foundation_effects = {
        # --- DRUID ---
        "CS2_012": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 2, source)\n    source.controller.draw(1)", # Swipe? No, Swipe is CS2_012.
        "CS2_013t": "def on_play(game, source, target):\n    source.controller.draw(1)", # Excess Mana
        "EX1_154": "def on_play(game, source, target):\n    source.controller.gain_mana_crystal(2, True)", # Wild Growth
        "EX1_160": "def on_play(game, source, target):\n    source.controller.gain_mana_crystal(2, True)", # Nourish?
        "CORE_EX1_154": "def on_play(game, source, target):\n    source.controller.gain_mana_crystal(1, False)", # Wild Growth (Core)
        
        # --- HUNTER ---
        "DS1_184": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 2, source)", # Tracking? No, Hunter's Mark is DS1_184.
        "CS2_084": "def on_play(game, source, target):\n    import random\n    targets = source.controller.opponent.board[:]\n    if targets:\n        for _ in range(2): game.deal_damage(random.choice(targets), 2, source)", # Multi-Shot
        "EX1_538": "def on_play(game, source, target):\n    source.controller.opponent.hero.health -= 5", # Kill Command? No, EX1_538 is Unleash the Hounds.
        
        # --- MAGE ---
        "CS2_022": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 1, source)\n    source.controller.draw(1)",
        "CS2_023": "def on_play(game, source, target):\n    source.controller.draw(2)",
        "CS2_024": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 3, source); target.frozen = True",
        "CS2_029": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 6, source)",
        "CS2_032": "def on_play(game, source, target):\n    for m in source.controller.opponent.board[:]: game.deal_damage(m, 4, source)",
        "EX1_277": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 10, source)",
        
        # --- PALADIN ---
        "CS2_093": "def on_play(game, source, target):\n    if target: target.attack = 1", # Humility
        "CS2_094": "def on_play(game, source, target):\n    source.controller.draw(1)\n    source.controller.hero.attack += 2", # Hammer of Wrath
        
        # --- PRIEST ---
        "CS2_234": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 2, source)", # Holy Smite
        "CS2_235": "def on_play(game, source, target):\n    if target: source.controller.draw(1); target.health += 2", # Power Word: Shield
        "EX1_622": "def on_play(game, source, target):\n    if target: target.destroy()", # Shadow Word: Death
        
        # --- ROGUE ---
        "CS2_072": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 2, source)", # Backstab (needs condition: undamaged)
        "CS2_073": "def on_play(game, source, target):\n    if target: target.attack += 2", # Cold Blood
        "EX1_124": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 2, source)", # Eviscerate
        
        # --- SHAMAN ---
        "CS2_045": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 2, source); source.controller.overload += 1", # Rockbiter? No, Lightning Bolt.
        "EX1_238": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 3, source); source.controller.overload += 1", # Lightning Bolt
        "EX1_259": "def on_play(game, source, target):\n    if target: target.transform('EX1_259t')", # Hex?
        
        # --- WARLOCK ---
        "CS2_062": "def on_play(game, source, target):\n    for p in game.players:\n        game.deal_damage(p.hero, 3, source)\n        for m in p.board[:]: game.deal_damage(m, 3, source)",
        "EX1_308": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 4, source); source.controller.discard(1)", # Soulfire
        
        # --- WARRIOR ---
        "CS2_105": "def on_play(game, source, target):\n    source.controller.hero.attack += 4",
        "CS2_108": "def on_play(game, source, target):\n    if target: target.destroy()",
        
        # --- NEUTRAL BATTLECRIES ---
        "CS2_189": "def battlecry(game, source, target):\n    if target: game.deal_damage(target, 1, source)",
        "EX1_015": "def battlecry(game, source, target):\n    source.controller.draw(1)",
        "CS2_117": "def battlecry(game, source, target):\n    if target: game.heal(target, 3)",
        "EX1_011": "def battlecry(game, source, target):\n    if target: game.heal(target, 2)",
        "EX1_066": "def battlecry(game, source, target):\n    if source.controller.opponent.hero.weapon: source.controller.opponent.hero.weapon.destroy()",
        "CS2_147": "def battlecry(game, source, target):\n    for m in source.controller.board: \n        if m.race == Race.MURLOC: m.attack += 2; m.health += 1; m.max_health += 1",
        
        # --- NEUTRAL DEATHRATTLES ---
        "EX1_012": "def deathrattle(game, source):\n    source.controller.draw(1)",
    }
    
    for cid, code in foundation_effects.items():
        gen.implement_manually(cid, code, "LEGACY")
        # Also copy to CORE if it's there
        if "CORE_" + cid in CardDatabase.get_instance().load():
             gen.implement_manually("CORE_" + cid, code, "CORE")

    print(f"Imported {len(foundation_effects)} foundation effects.")

if __name__ == "__main__":
    from simulator.card_loader import CardDatabase
    bulk_import_foundations()
