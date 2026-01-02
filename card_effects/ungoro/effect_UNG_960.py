"""Effect for UNG_960 in UNGORO"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CS2_101t', source.zone_position + 1)
    game.summon_token(source.controller, 'CS2_101t', source.zone_position + 2)
