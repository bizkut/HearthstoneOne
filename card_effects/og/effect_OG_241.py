"""Effect for OG_241 in OG"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_241a', source.zone_position + 1)
