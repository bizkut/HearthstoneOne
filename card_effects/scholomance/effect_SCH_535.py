"""Effect for SCH_535 in SCHOLOMANCE"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 3, source)