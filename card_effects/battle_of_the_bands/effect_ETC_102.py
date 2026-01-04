"""Effect for ETC_102 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    if source.controller.weapon: source.controller.weapon.durability += 1