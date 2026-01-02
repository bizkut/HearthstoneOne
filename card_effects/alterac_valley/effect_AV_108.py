"""Effect for AV_108 in ALTERAC_VALLEY"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 5, source)