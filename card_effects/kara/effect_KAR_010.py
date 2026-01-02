"""Effect for KAR_010 in KARA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'KAR_010a', source.zone_position + 1)
    game.summon_token(source.controller, 'KAR_010a', source.zone_position + 2)
