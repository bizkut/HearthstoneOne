"""Effect for TOY_354 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)