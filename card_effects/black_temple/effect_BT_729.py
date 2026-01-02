"""Effect for BT_729 in BLACK_TEMPLE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)