"""Effect for REV_356 in REVENDRETH"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TRL_020t', source.zone_position + 1)
