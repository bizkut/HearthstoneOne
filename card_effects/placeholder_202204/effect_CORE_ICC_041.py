"""Effect for CORE_ICC_041 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 1, source)