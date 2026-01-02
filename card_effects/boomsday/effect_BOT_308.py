"""Effect for BOT_308 in BOOMSDAY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)