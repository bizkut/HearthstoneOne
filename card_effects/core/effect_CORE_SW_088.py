"""Effect for CORE_SW_088 in CORE"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CS2_065', source.zone_position + 1)
    game.summon_token(source.controller, 'CS2_065', source.zone_position + 2)
