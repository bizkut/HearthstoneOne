"""Effect for GVG_009 in GVG"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)