"""Effect for RLK_956 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'WON_076t', source.zone_position + 1)
