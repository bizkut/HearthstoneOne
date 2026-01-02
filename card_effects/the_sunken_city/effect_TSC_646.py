"""Effect for TSC_646 in THE_SUNKEN_CITY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TSC_646t', source.zone_position + 1)
    game.summon_token(source.controller, 'TSC_646t', source.zone_position + 2)
