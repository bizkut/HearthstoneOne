"""Effect for EX1_066 in LEGACY"""

def battlecry(game, source, target):
    if source.controller.opponent and source.controller.opponent.weapon:
        source.controller.opponent.weapon.destroy()