"""Effect for TOY_826 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 1, source)