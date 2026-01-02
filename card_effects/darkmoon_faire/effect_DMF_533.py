"""Effect for DMF_533 in DARKMOON_FAIRE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 1)
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 2)
