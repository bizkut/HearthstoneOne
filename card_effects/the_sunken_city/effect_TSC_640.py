"""Effect for TSC_640 in THE_SUNKEN_CITY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TSC_638t4', source.zone_position + 1)
