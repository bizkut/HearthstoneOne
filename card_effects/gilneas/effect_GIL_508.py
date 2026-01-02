"""Effect for GIL_508 in GILNEAS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TRL_020t', source.zone_position + 1)
    game.summon_token(source.controller, 'TRL_020t', source.zone_position + 2)
