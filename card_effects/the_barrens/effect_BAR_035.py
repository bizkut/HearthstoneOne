"""Effect for BAR_035 in THE_BARRENS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 1)
