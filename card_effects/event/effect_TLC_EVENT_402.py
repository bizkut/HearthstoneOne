"""Effect for TLC_EVENT_402 in EVENT"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: m.destroy()