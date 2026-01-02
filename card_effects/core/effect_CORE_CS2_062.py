"""Effect for CORE_CS2_062 in CORE"""

def on_play(game, source, target):
    for p in game.players:
        game.deal_damage(p.hero, 3, source)
        for m in p.board[:]: game.deal_damage(m, 3, source)