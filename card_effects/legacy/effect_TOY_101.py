"""Effect for TOY_101 in LEGACY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)