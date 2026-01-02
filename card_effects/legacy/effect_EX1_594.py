"""Effect for EX1_594 in LEGACY"""

def on_play(game, source, target):
    for p in game.players: 
        for m in p.board[:]: m.frozen = True