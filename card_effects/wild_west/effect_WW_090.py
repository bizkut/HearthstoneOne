"""Effect for WW_090 in WILD_WEST"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 6, source)