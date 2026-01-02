"""Effect for CFM_647 in GANGS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)