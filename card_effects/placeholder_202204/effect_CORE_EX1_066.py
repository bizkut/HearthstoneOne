"""Effect for CORE_EX1_066 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    if source.controller.opponent and source.controller.opponent.weapon:
        source.controller.opponent.weapon.destroy()