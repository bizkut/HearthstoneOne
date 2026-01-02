"""Effect for CORE_CS2_189 in CORE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)