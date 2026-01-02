"""Effect for SW_093 in STORMWIND"""

def battlecry(game, source, target):
    source.controller.hero.attack += 2