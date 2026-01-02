"""Effect for BAR_060 in THE_BARRENS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BAR_060t', source.zone_position + 1)
