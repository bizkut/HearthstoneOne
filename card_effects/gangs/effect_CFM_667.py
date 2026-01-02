"""Effect for CFM_667 in GANGS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)