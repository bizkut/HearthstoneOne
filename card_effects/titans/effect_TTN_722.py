"""Effect for TTN_722 in TITANS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)