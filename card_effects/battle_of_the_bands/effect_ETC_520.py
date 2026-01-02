"""Effect for ETC_520 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)