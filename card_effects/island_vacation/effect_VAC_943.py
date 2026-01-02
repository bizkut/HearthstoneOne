"""Effect for VAC_943 in ISLAND_VACATION"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 1)
