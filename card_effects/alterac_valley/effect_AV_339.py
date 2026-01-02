"""Effect for AV_339 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_130a', source.zone_position + 1)
