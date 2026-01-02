"""Effect for GIL_825 in GILNEAS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)