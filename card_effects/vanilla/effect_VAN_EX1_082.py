"""Effect for VAN_EX1_082 in VANILLA"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)