"""Effect for BAR_306 in THE_BARRENS"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 3, source)