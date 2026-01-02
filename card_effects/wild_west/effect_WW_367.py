"""Effect for WW_367 in WILD_WEST"""

def battlecry(game, source, target):
    if target: target.attack += 1; target.max_health += 1; target.health += 1