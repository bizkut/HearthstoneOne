"""Effect for VAC_953 in ISLAND_VACATION"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 2, source)