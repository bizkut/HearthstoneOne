"""Effect for AT_105 in TGT"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)