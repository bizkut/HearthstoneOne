"""Effect for FP1_002 in NAXX"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'FP1_002t', source.zone_position + 1)
    game.summon_token(source.controller, 'FP1_002t', source.zone_position + 2)
