"""Effect for CORE_REV_906 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)