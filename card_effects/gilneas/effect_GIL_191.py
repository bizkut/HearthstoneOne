"""Effect for GIL_191 in GILNEAS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 1)
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 2)
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 3)
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 4)
