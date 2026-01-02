"""Effect for WW_434 in WILD_WEST"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 6, source)