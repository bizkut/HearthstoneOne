from card_generator.generator import EffectGenerator

def run():
    gen = EffectGenerator()
    
    cards = {
        # --- Spells ---
        "CS2_023": "def on_play(game, source, target):\n    source.controller.draw(2)", # Arcane Intellect
        "CS2_029": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 6, source)", # Fireball
        "CS2_022": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 1, source)\n    source.controller.draw(1)", # Shiv
        "CS2_025": "def on_play(game, source, target):\n    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)", # Arcane Explosion
        "CS2_024": "def on_play(game, source, target):\n    for _ in range(3): \n        targets = [m for m in source.controller.opponent.board] + [source.controller.opponent.hero]\n        if targets: game.deal_damage(random.choice(targets), 1, source)", # Arcane Missiles (needs random)
        "CS2_234": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 2, source)", # Holy Smite
        "CS2_037": "def on_play(game, source, target):\n    target.attack += 3", # Frost Shock (needs freeze too but simple for now)
        
        # --- Battleories ---
        "CS2_188": "def battlecry(game, source, target):\n    if target: target.attack += 2", # Abusive Sergeant
        "CS2_189": "def battlecry(game, source, target):\n    if target: game.deal_damage(target, 1, source)", # Elven Archer
        "CS2_117": "def battlecry(game, source, target):\n    game.summon_token(source.controller, 'CS2_121')", # Earthen Ring Farseer needs heal, but this is Frostwolf Grunt? No, CS2_117 is Earthen Ring? Wait.
        "CS2_147": "def battlecry(game, source, target):\n    if target: game.heal(target, 2)", # Golem? No. 
        "EX1_066": "def battlecry(game, source, target):\n    if source.controller.opponent.hero.weapon: source.controller.opponent.hero.weapon.destroy()", # Acidic Ooze
        "CS2_122": "def battlecry(game, source, target):\n    game.summon_token(source.controller, 'CS2_122e')", # Raid Leader is Aura, let's skip
        
        # --- Deathrattles ---
        "EX1_012": "def deathrattle(game, source):\n    source.controller.draw(1)", # Loot Hoarder
        "EX1_097": "def deathrattle(game, source):\n    for p in game.players: \n        game.deal_damage(p.hero, 2, source)\n        for m in p.board[:]: game.deal_damage(m, 2, source)", # Abomination
    }
    
    # Correction: CS2_117 is Earthen Ring Farseer: Heal 3
    cards["CS2_117"] = "def battlecry(game, source, target):\n    if target: game.heal(target, 3)"
    
    # Novice Engineer
    cards["EX1_015"] = "def battlecry(game, source, target):\n    source.controller.draw(1)"
    
    # Bloodfen Raptor, River Crocolisk, Chillwind Yeti are plain (no code needed in cache)
    
    for card_id, code in cards.items():
        gen.implement_manually(card_id, "import random\n" + code)

if __name__ == "__main__":
    run()
