"""Effect for GVG_076 in GVG"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 2, source)