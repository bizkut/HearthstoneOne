"""Effect for CORE_GIL_622 in CORE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)