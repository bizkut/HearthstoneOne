"""Effect for CORE_REV_840 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 2, source)