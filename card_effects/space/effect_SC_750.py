"""Effect for SC_750 in SPACE"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'SC_751t', source.zone_position + 1)
