"""Effect for CS2_064 in LEGACY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)