"""Effect for LOOT_077 in LOOTAPALOOZA"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'LOOT_077t', source.zone_position + 1)
