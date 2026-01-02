"""Effect for DMF_238 in DARKMOON_FAIRE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'DMF_238t', source.zone_position + 1)
