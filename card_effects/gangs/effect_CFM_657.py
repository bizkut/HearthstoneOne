"""Effect for CFM_657 in GANGS"""

def battlecry(game, source, target):
    if target: target.silence()