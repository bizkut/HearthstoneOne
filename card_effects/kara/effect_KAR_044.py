"""Effect for KAR_044 in KARA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'KAR_044a', source.zone_position + 1)
