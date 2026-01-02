"""Effect for VAN_CS2_188 in VANILLA"""

import random
def battlecry(game, source, target):
    if target: target.attack += 2