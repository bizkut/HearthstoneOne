"""Effect for REV_827 in REVENDRETH"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'OG_216a', source.zone_position + 1)
