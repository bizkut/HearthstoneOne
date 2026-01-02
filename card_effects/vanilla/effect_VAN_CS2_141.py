"""Effect for VAN_CS2_141 in VANILLA"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)