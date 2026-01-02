"""Effect for CORE_CS2_117 in CORE"""

def battlecry(game, source, target):
    if target: game.heal(target, 3)