"""Effect for FP1_021 in NAXX"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 1, source)