"""Effect for AV_211 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'LOOT_077t', source.zone_position + 1)
