"""Effect for CORE_EX1_066 in CORE"""

def battlecry(game, source, target):
    if source.controller.opponent.hero.weapon: source.controller.opponent.hero.weapon.destroy()