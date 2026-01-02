"""Effect for CORE_ICC_021 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 2, source)