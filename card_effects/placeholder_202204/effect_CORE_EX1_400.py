"""Effect for CORE_EX1_400 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    for p in game.players: 
        for m in p.board[:]: game.deal_damage(m, 1, source)