"""Effect for BT_009 in BLACK_TEMPLE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 1)
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 2)
