"""Effect for TOY_377 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)