"""Effect for REV_012 in REVENDRETH"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'REV_012t', source.zone_position + 1)
