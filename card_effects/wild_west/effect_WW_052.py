"""Effect for WW_052 in WILD_WEST"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)