"""Effect for SW_431 in STORMWIND"""

def battlecry(game, source, target):
    source.controller.hero.attack += 3