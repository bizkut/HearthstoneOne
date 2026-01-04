"""Effect for DEEP_012 in WILD_WEST"""


def battlecry(game, source, target):
    if source.controller.weapon:
        w = source.controller.weapon
        source.attack += w.attack
        source.max_health += w.durability
        source.health += w.durability
        # Simplified: doesn't "give it back" yet
