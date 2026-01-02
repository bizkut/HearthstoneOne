"""Effect for VAC_323 in ISLAND_VACATION"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)