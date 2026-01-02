"""Effect for EX1_097 in EXPERT1"""

def deathrattle(game, source):
    for p in game.players: 
        game.deal_damage(p.hero, 2, source)
        for m in p.board[:]: game.deal_damage(m, 2, source)