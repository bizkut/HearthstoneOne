"""Effect for UNG_010 in UNGORO"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 1)
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 2)
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 3)
