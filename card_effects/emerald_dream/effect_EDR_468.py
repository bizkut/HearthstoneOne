"""Effect for EDR_468 in EMERALD_DREAM"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)