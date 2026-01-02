"""Effect for EX1_603_battlecry in LEGACY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source); target.attack += 2