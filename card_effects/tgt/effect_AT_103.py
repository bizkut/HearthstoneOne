"""Effect for AT_103 in TGT"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 4, source)