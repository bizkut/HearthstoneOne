"""Effect for ETC_086 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 3, source)