"""Effect for OG_216 in OG"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_216a', source.zone_position + 1)
    game.summon_token(source.controller, 'OG_216a', source.zone_position + 2)
