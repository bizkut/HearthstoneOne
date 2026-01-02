"""Effect for AT_094 in TGT"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)