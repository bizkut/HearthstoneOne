"""Effect for REV_013 in REVENDRETH"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)