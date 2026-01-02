"""Effect for CORE_RLK_708 in CORE"""

def battlecry(game, source, target):
    source.controller.draw(1)
def deathrattle(game, source):
    source.controller.draw(1)