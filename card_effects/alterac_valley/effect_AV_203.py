"""Effect for AV_203 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULD_286t', source.zone_position + 1)
    game.summon_token(source.controller, 'ULD_286t', source.zone_position + 2)
