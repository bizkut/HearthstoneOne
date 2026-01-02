"""Effect for DEEP_012 in WILD_WEST"""


def battlecry(game, source, target):
    if source.controller.hero.weapon:
        w = source.controller.hero.weapon
        source.attack += w.attack
        source.max_health += w.durability
        source.health += w.durability
        # Simplified: doesn't "give it back" yet
