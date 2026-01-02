"""Effect for ICC_047 in ICECROWN"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 3, source)