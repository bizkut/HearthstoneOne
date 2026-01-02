"""Effect for VAN_EX1_534 in VANILLA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 1)
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 2)
