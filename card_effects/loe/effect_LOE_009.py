"""Effect for LOE_009 in LOE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'WON_079t2', source.zone_position + 1)
