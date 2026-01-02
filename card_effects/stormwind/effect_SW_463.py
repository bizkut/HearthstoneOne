"""Effect for SW_463 in STORMWIND"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_216a', source.zone_position + 1)
    game.summon_token(source.controller, 'OG_216a', source.zone_position + 2)
