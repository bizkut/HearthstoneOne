"""Effect for EX1_066 in LEGACY"""

def battlecry(game, source, target):
    if source.controller.opponent.hero.weapon: source.controller.opponent.hero.weapon.destroy()