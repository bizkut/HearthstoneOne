"""Effect for REV_840 in REVENDRETH"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 2, source)