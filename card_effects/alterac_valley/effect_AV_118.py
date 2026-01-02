"""Effect for AV_118 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BT_922t', source.zone_position + 1)
    game.summon_token(source.controller, 'BT_922t', source.zone_position + 2)
