"""Effect for DRG_307 in DRAGONS"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 2, source)