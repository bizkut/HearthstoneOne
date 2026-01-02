"""Effect for CORE_CS2_088 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    if target: game.heal(target, 6)