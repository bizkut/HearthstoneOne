"""Effect for VAN_NEW1_021 in VANILLA"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: m.destroy()