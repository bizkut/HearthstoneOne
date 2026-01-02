"""Effect for CORE_FP1_007 in CORE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'WON_076t', source.zone_position + 1)
