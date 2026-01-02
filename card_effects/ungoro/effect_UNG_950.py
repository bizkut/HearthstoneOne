"""Effect for UNG_950 in UNGORO"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CS2_101t', source.zone_position + 1)
    game.summon_token(source.controller, 'CS2_101t', source.zone_position + 2)
