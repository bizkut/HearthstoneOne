"""Effect for SW_431 in STORMWIND"""

def battlecry(game, source, target):
    source.controller.add_hero_attack(3)