"""Effect for BT_155 in BLACK_TEMPLE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BT_155t', source.zone_position + 1)
