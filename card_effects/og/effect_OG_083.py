"""Effect for OG_083 in OG"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)