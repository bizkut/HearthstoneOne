"""Effect for CS2_141 in LEGACY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)