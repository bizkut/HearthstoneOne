"""Effect for UNG_848 in UNGORO"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)