"""Effect for TLC_478 in THE_LOST_CITY"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 1, source)