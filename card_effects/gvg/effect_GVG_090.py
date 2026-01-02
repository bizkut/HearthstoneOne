"""Effect for GVG_090 in GVG"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 6, source)