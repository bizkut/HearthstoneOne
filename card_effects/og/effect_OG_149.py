"""Effect for OG_149 in OG"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)