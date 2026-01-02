"""Effect for LOOT_026 in LOOTAPALOOZA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_216a', source.zone_position + 1)
