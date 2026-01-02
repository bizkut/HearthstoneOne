"""Effect for VAC_305 in ISLAND_VACATION"""


def on_play(game, source, target):
    game.summon_token(source.controller, 'VAC_305t', 0)
    game.summon_token(source.controller, 'VAC_305t', 0)
