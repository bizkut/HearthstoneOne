"""Effect for LEG_RLK_079 in LEGACY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)