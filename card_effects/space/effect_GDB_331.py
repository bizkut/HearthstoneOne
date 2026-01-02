"""Effect for GDB_331 in SPACE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'GDB_331t1', source.zone_position + 1)
    game.summon_token(source.controller, 'GDB_331t1', source.zone_position + 2)
