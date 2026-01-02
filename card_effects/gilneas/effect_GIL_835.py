"""Effect for GIL_835 in GILNEAS"""

def battlecry(game, source, target):
    if target: game.heal(target, 2)