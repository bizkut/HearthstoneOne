"""Effect for GVG_110 in GVG"""


def battlecry(game, source, target):
    game.summon_token(source.controller, 'GVG_110t', source.zone_position + 1)
    game.summon_token(source.controller, 'GVG_110t', source.zone_position + 2)
