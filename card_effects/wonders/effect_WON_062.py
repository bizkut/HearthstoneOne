"""Effect for WON_062 in WONDERS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)