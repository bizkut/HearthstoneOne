"""Effect for CORE_EX1_323 in CORE"""

def battlecry(game, source, target):
    # Simplified: doesn't replace hero entity, just stats
    source.controller.hero.health = 15; source.controller.hero.max_health = 15