"""Effect for WON_127 in WONDERS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)