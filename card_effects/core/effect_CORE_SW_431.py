"""Effect for CORE_SW_431 in CORE"""

def battlecry(game, source, target):
    source.controller.add_hero_attack(3)