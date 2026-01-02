"""Effect for DS1_055 in LEGACY"""

def battlecry(game, source, target):
    if target: game.heal(target, 2)