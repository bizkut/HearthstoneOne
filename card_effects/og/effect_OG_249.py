"""Effect for OG_249 in OG"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_314b', source.zone_position + 1)
