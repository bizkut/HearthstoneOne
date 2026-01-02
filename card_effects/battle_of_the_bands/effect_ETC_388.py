"""Effect for ETC_388 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)