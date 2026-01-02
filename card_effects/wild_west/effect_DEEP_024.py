"""Effect for DEEP_024 in WILD_WEST"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)