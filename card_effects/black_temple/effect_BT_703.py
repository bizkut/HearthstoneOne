"""Effect for BT_703 in BLACK_TEMPLE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULD_286t', source.zone_position + 1)
