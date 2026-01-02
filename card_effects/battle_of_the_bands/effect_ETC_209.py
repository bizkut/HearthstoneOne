"""Effect for ETC_209 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)