"""Effect for TIME_009 in TIME_TRAVEL"""


def battlecry(game, source, target):
    # Put aura from deck to battlefield - simplified: draw 2 spells
    source.controller.draw(2)
