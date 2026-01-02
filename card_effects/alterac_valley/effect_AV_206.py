"""Effect for AV_206 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)