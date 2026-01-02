"""Effect for VAN_EX1_614 in VANILLA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_TU4e_002t', source.zone_position + 1)
