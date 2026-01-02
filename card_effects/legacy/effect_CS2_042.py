"""Effect for CS2_042 in LEGACY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 4, source)