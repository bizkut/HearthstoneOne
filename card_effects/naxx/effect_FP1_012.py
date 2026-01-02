"""Effect for FP1_012 in NAXX"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_314b', source.zone_position + 1)
