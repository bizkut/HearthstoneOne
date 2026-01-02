"""Effect for TRL_512 in TROLL"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)