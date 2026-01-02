"""Effect for BAR_871 in THE_BARRENS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CS2_101t', source.zone_position + 1)
    game.summon_token(source.controller, 'CS2_101t', source.zone_position + 2)
