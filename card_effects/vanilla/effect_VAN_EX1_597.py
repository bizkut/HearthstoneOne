"""Effect for VAN_EX1_597 in VANILLA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 1)
