"""Effect for DMF_174 in DARKMOON_FAIRE"""

def battlecry(game, source, target):
    if target: game.heal(target, 4)