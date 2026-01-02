"""Effect for REV_314 in REVENDRETH"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'KAR_010a', source.zone_position + 1)
