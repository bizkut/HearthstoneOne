"""Effect for RLK_659 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    source.controller.hero.gain_armor(5)