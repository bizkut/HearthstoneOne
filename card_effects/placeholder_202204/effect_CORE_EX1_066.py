"""Effect for CORE_EX1_066 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    if source.controller.opponent.hero.weapon: source.controller.opponent.hero.weapon.destroy()