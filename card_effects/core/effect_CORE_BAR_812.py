"""Effect for CORE_BAR_812 in CORE"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'VAC_509t', source.zone_position + 1)
