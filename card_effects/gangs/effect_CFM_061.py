"""Effect for CFM_061 in GANGS"""

def battlecry(game, source, target):
    if target: game.heal(target, 6)