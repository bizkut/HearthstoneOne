"""Effect for EDR_262 in EMERALD_DREAM"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'LOOT_077t', source.zone_position + 1)
