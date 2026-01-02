"""Effect for TLC_429 in THE_LOST_CITY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 1)
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 2)
