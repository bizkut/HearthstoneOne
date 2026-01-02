"""Effect for VAC_926 in ISLAND_VACATION"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)