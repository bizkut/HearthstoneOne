"""Effect for RLK_552 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'RLK_060t', source.zone_position + 1)
    game.summon_token(source.controller, 'RLK_060t', source.zone_position + 2)
