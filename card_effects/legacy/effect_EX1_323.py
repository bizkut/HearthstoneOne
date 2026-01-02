"""Effect for EX1_323 in LEGACY"""

def battlecry(game, source, target):
    # Simplified: doesn't replace hero entity, just stats
    source.controller.hero.health = 15; source.controller.hero.max_health = 15