"""Effect for EDR_570 in EMERALD_DREAM"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 1, source)