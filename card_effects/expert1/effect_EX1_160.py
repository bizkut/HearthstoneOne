"""Effect for EX1_160 in EXPERT1"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'EX1_160t', source.zone_position + 1)
