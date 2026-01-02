"""Effect for CORE_EX1_319 in CORE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)