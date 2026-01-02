"""Effect for CORE_CS2_042 in CORE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 4, source)