"""Effect for UNG_084 in UNGORO"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)