"""Effect for WORK_028 in ISLAND_VACATION"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: m.destroy()