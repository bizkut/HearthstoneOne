"""Effect for BT_717 in BLACK_TEMPLE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)