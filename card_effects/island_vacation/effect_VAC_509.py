"""Effect for VAC_509 in ISLAND_VACATION"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)