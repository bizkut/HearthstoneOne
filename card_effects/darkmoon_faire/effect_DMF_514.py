"""Effect for DMF_514 in DARKMOON_FAIRE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'DMF_514t2', source.zone_position + 1)
