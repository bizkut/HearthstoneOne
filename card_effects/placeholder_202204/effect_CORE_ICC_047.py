"""Effect for CORE_ICC_047 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 3, source)