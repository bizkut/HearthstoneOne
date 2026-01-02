"""Effect for EDR_523 in EMERALD_DREAM"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'OG_216a', source.zone_position + 1)
