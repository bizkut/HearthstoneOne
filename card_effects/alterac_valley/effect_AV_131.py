"""Effect for AV_131 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)