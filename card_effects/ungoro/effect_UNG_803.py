"""Effect for UNG_803 in UNGORO"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)