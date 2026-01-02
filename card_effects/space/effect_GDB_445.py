"""Effect for GDB_445 in SPACE"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 5, source)