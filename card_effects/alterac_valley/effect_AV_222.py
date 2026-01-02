"""Effect for AV_222 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)