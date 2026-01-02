"""Effect for WW_024 in WILD_WEST"""


def battlecry(game, source, target):
    game.summon_token(source.controller, 'WW_024t', source.zone_position + 1)
    game.summon_token(source.controller, 'WW_024t', source.zone_position + 2)
