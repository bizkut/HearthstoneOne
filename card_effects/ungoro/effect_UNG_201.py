"""Effect for UNG_201 in UNGORO"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 1)
