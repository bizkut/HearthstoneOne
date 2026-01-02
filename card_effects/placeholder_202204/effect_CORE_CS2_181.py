"""Effect for CORE_CS2_181 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 4, source)