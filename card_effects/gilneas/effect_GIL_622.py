"""Effect for GIL_622 in GILNEAS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)