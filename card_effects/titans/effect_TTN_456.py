"""Effect for TTN_456 in TITANS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)