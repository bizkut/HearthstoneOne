"""Effect for SW_093 in STORMWIND"""

def battlecry(game, source, target):
    source.controller.add_hero_attack(2)