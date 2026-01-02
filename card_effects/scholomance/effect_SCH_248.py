"""Effect for SCH_248 in SCHOLOMANCE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)