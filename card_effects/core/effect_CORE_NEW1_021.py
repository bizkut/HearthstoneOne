"""Effect for CORE_NEW1_021 in CORE"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: m.destroy()