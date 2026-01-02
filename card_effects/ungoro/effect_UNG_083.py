"""Effect for UNG_083 in UNGORO"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_tk29', source.zone_position + 1)
