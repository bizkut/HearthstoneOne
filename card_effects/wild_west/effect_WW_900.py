"""Effect for WW_900 in WILD_WEST"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)