"""Effect for BAR_801 in THE_BARRENS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 1)
