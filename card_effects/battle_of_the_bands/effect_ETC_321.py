"""Effect for ETC_321 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULDA_Reno_05', source.zone_position + 1)
    game.summon_token(source.controller, 'ULDA_Reno_05', source.zone_position + 2)
    game.summon_token(source.controller, 'ULDA_Reno_05', source.zone_position + 3)
