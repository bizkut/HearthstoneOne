"""Effect for AV_309 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 1)
