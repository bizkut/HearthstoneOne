"""Effect for BAR_812 in THE_BARRENS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'VAC_509t', source.zone_position + 1)
