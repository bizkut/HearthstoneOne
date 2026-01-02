"""Effect for CORE_LOOT_026 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_216a', source.zone_position + 1)
