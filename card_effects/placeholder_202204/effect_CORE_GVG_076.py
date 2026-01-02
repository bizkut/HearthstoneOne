"""Effect for CORE_GVG_076 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 2, source)