"""Effect for BT_723 in BLACK_TEMPLE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)