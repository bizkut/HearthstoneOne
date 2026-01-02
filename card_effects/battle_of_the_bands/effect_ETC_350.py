"""Effect for ETC_350 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    if target: target.attack += 1; target.max_health += 1; target.health += 1