"""Effect for VAN_EX1_312 in VANILLA"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: m.destroy()