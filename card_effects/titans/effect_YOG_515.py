"""Effect for YOG_515 in TITANS"""


def battlecry(game, source, target):
    game.summon_token(source.controller, 'YOG_514t', source.zone_position + 1)
    game.summon_token(source.controller, 'YOG_514t', source.zone_position + 2)
