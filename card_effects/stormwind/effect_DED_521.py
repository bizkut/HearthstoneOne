"""Effect for DED_521 in STORMWIND"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 12, source)