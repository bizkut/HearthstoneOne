"""Effect for VAN_EX1_133 in VANILLA"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)