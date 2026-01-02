"""Effect for CORE_EX1_011 in CORE"""

def battlecry(game, source, target):
    if target: game.heal(target, 2)