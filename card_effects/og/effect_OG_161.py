"""Effect for OG_161 in OG"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)