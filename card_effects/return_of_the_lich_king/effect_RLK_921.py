"""Effect for RLK_921 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)