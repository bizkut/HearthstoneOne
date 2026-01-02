"""Effect for DMF_110 in DARKMOON_FAIRE"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 2, source)