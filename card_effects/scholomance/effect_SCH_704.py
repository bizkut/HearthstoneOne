"""Effect for SCH_704 in SCHOLOMANCE"""

def battlecry(game, source, target):
    source.controller.add_hero_attack(5)