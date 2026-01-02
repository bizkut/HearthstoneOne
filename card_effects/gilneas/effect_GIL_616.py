"""Effect for GIL_616 in GILNEAS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'GIL_616t', source.zone_position + 1)
    game.summon_token(source.controller, 'GIL_616t', source.zone_position + 2)
