"""Effect for OG_156 in OG"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_156a', source.zone_position + 1)
