"""Effect for TTN_950 in TITANS"""


def on_play(game, source, target):
    game.summon_token(source.controller, 'TTN_950t', source.zone_position + 1)
    game.summon_token(source.controller, 'TTN_950t', source.zone_position + 2)
