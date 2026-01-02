"""Effect for AV_316 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 3, source)