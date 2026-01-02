"""Effect for TTN_478 in TITANS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)