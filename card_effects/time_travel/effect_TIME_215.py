"""Effect for TIME_215 in TIME_TRAVEL"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 1, source)