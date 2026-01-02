"""Effect for VAN_CS2_150 in VANILLA"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)