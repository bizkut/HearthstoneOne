"""Effect for CORE_ULD_271 in CORE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)