"""Effect for CORE_OG_241 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_241a', source.zone_position + 1)
