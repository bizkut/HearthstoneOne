"""Effect for DRG_067 in DRAGONS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)