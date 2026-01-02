"""Effect for OG_162 in OG"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)