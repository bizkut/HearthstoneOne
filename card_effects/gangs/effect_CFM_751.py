"""Effect for CFM_751 in GANGS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)