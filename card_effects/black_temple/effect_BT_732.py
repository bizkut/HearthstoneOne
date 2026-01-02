"""Effect for BT_732 in BLACK_TEMPLE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 6, source)