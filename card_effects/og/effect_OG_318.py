"""Effect for OG_318 in OG"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TU4a_003', source.zone_position + 1)
