"""Effect for TRL_503 in TROLL"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'WON_079t2', source.zone_position + 1)
    game.summon_token(source.controller, 'WON_079t2', source.zone_position + 2)
    game.summon_token(source.controller, 'WON_079t2', source.zone_position + 3)
