"""Effect for BT_722 in BLACK_TEMPLE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)