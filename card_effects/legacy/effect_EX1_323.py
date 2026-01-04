"""Effect for EX1_323 in LEGACY"""

def battlecry(game, source, target):
    # Simplified: doesn't replace hero entity, just stats
    source.controller.set_hero_health(15)