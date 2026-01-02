"""Effect for TRL_546 in TROLL"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)