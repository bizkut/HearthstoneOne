"""Effect for BOT_104 in BOOMSDAY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)