"""Effect for VAN_EX1_066 in VANILLA"""

def battlecry(game, source, target):
    if source.controller.opponent and source.controller.opponent.weapon:
        source.controller.opponent.weapon.destroy()