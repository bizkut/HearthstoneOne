"""Effect for OG_272 in OG"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_272t', source.zone_position + 1)
