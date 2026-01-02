"""Effect for RLK_035 in RETURN_OF_THE_LICH_KING"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 1, source)