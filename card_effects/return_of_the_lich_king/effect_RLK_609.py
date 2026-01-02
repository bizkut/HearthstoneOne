"""Effect for RLK_609 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 1, source)