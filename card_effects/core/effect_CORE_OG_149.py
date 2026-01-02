"""Effect for CORE_OG_149 in CORE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)