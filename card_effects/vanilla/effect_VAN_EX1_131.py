"""Effect for VAN_EX1_131 in VANILLA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EX1_131t', source.zone_position + 1)
