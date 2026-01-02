"""Effect for EX1_573 in EXPERT1"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_tk9b', source.zone_position + 1)
    game.summon_token(source.controller, 'VAN_EX1_tk9b', source.zone_position + 2)
