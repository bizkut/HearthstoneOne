"""Effect for SCH_253 in SCHOLOMANCE"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 3, source)