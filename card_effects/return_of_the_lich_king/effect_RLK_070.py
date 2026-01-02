"""Effect for RLK_070 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'RLK_Prologue_RLK_070t', source.zone_position + 1)
