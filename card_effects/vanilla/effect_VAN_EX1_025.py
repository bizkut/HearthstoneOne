"""Effect for VAN_EX1_025 in VANILLA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EX1_025t', source.zone_position + 1)
