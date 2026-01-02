"""Effect for ETC_526 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TB_BotB_BlightBoar', source.zone_position + 1)
