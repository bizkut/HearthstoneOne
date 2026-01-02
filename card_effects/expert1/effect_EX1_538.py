"""Effect for EX1_538 in EXPERT1"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'EX1_538t', source.zone_position + 1)
