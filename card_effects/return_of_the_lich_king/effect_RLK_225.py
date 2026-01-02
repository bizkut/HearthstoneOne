"""Effect for RLK_225 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'RLK_060t', source.zone_position + 1)
