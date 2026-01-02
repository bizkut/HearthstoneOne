"""Effect for TLC_234 in THE_LOST_CITY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TLC_234t', source.zone_position + 1)
