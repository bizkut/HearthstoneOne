"""Effect for ETC_411 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    game.summon_token(source.controller, 'ETC_411t', source.zone_position + 1)
    game.summon_token(source.controller, 'ETC_411t', source.zone_position + 2)
    # Outcast simplified
    # if source.is_outer_most(): game.summon_token(...)
