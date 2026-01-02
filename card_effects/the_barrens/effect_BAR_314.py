"""Effect for BAR_314 in THE_BARRENS"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)