"""Effect for EX1_025 in LEGACY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EX1_025t', source.zone_position + 1)
