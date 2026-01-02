"""Effect for CORE_SW_107 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 3, source)