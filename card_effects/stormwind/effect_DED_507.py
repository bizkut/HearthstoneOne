"""Effect for DED_507 in STORMWIND"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)