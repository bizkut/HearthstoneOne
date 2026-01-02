"""Effect for WC_008 in THE_BARRENS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 1)
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 2)
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 3)
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 4)
