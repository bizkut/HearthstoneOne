"""Effect for TSC_924 in THE_SUNKEN_CITY"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 4, source)