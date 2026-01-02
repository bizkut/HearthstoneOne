"""Effect for SW_107 in STORMWIND"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 3, source)