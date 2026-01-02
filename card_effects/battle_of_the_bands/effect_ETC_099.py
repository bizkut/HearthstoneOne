"""Effect for ETC_099 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    if target: target.destroy()