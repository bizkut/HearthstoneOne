"""Effect for CORE_BOT_104 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)