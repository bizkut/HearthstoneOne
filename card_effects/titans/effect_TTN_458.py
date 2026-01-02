"""Effect for TTN_458 in TITANS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)