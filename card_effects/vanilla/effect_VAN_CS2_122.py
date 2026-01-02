"""Effect for VAN_CS2_122 in VANILLA"""

import random
def battlecry(game, source, target):
    game.summon_token(source.controller, 'CS2_122e')