"""Effect for CORE_UNG_205 in CORE"""

def battlecry(game, source, target):
    if target: target.frozen = True