"""Effect for CORE_BAR_801 in CORE"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 1)
