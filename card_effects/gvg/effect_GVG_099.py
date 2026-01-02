"""Effect for GVG_099 in GVG"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 4, source)