"""Effect for SW_066 in STORMWIND"""

def battlecry(game, source, target):
    if target: target.silence()