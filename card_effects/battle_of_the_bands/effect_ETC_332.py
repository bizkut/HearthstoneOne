"""Effect for ETC_332 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    if target: game.heal(target, 3)