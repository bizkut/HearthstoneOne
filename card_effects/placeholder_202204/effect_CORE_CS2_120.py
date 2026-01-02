"""Effect for CORE_CS2_120 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    if target: target.attack += 1; target.health += 1