"""Effect for NEW1_021 in EXPERT1"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: m.destroy()