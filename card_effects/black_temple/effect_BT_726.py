"""Effect for BT_726 in BLACK_TEMPLE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BT_726t', source.zone_position + 1)
