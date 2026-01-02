"""Effect for RLK_219 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    if target: game.heal(target, 3)