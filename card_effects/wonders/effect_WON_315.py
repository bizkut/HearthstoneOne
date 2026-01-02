"""Effect for WON_315 in WONDERS"""

def battlecry(game, source, target):
    if target: game.heal(target, 5)