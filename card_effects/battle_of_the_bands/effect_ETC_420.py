"""Effect for ETC_420 in BATTLE_OF_THE_BANDS"""


def battlecry(game, source, target):
    if target:
        target.attack += source.attack
        target.max_health += source.health
        target.health += source.health
