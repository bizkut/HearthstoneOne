"""Effect for EX1_556 in EXPERT1"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_skele21', source.zone_position + 1)
