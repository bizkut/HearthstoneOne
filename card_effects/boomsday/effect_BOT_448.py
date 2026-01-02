"""Effect for BOT_448 in BOOMSDAY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 6, source)