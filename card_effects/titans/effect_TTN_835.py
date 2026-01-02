"""Effect for TTN_835 in TITANS"""


def battlecry(game, source, target):
    # Unlock Overload (simplified)
    source.controller.draw(2) # Drawing some as compensation for the count
