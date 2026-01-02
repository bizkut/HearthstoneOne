"""Effect for CORE_ULD_191 in CORE"""

def battlecry(game, source, target):
    if target: target.max_health += 2; target.health += 2