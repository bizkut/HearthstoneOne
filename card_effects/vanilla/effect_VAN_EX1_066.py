"""Effect for VAN_EX1_066 in VANILLA"""

def battlecry(game, source, target):
    if source.controller.opponent.hero.weapon: source.controller.opponent.hero.weapon.destroy()