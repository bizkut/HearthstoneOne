"""Effect for VAC_514 in ISLAND_VACATION"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAC_514t', source.zone_position + 1)
