"""Effect for ULD_181 in ULDUM"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 5, source)