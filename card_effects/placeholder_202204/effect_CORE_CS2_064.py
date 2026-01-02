"""Effect for CORE_CS2_064 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)