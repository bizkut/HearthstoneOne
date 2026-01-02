"""Effect for AT_100 in TGT"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CS2_101t', source.zone_position + 1)
