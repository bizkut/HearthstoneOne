"""Effect for TRL_531 in TROLL"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TRL_531t', source.zone_position + 1)
