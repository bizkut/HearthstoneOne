"""Effect for VAN_EX1_110 in VANILLA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_110t', source.zone_position + 1)
