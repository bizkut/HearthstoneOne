"""Effect for TLC_601 in THE_LOST_CITY"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 1, source)