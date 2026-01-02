"""Effect for FP1_014 in NAXX"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'NAX13_01H', source.zone_position + 1)
