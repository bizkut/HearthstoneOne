"""Effect for CORE_CFM_061 in CORE"""

def battlecry(game, source, target):
    if target: game.heal(target, 6)