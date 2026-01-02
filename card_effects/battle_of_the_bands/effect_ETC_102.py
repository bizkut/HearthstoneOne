"""Effect for ETC_102 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    if source.controller.hero.weapon: source.controller.hero.weapon.durability += 1