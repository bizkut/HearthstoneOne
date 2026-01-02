"""Effect for CORE_CS2_122 in CORE"""

import random
def battlecry(game, source, target):
    game.summon_token(source.controller, 'CS2_122e')