"""Effect for CORE_SW_066 in CORE"""

def battlecry(game, source, target):
    if target: target.silence()