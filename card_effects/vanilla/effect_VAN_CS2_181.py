"""Effect for VAN_CS2_181 in VANILLA"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 4, source)