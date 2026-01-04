"""Effect for CORE_EX1_323 in CORE"""

def battlecry(game, source, target):
    # Simplified: doesn't replace hero entity, just stats
    source.controller.set_hero_health(15)