"""Effect for UNG_076 in UNGORO"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'UNG_076t1', source.zone_position + 1)
    game.summon_token(source.controller, 'UNG_076t1', source.zone_position + 2)
