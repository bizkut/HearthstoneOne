"""Effect for CORE_TOY_101 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)