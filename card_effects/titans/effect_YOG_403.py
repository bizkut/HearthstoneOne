"""Effect for YOG_403 in TITANS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_tk9b', source.zone_position + 1)
