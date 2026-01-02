"""Effect for YOG_402 in TITANS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)