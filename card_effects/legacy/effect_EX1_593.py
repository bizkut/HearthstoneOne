"""Effect for EX1_593 in LEGACY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)