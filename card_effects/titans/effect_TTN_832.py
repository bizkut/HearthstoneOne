"""Effect for TTN_832 in TITANS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 4, source)