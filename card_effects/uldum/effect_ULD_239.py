"""Effect for ULD_239 in ULDUM"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 3, source)