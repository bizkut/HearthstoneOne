"""Effect for EX1_597 in EXPERT1"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 1)
