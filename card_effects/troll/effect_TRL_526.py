"""Effect for TRL_526 in TROLL"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)