"""Effect for TLC_447 in THE_LOST_CITY"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 2, source)