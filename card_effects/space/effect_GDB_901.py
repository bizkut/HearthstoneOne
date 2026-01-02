"""Effect for GDB_901 in SPACE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)