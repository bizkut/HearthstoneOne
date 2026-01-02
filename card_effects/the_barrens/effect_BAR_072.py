"""Effect for BAR_072 in THE_BARRENS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BAR_072t', source.zone_position + 1)
