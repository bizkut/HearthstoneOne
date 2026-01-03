"""Effect for VAN_CS2_037 in VANILLA"""

import random
def on_play(game, source, target):
    if target:
        target.attack += 3