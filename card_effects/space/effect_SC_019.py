"""Effect for SC_019 in SPACE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'SC_006', source.zone_position + 1)
