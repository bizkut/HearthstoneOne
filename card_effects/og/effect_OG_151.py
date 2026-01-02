"""Effect for OG_151 in OG"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 1, source)