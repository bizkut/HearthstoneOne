"""Effect for TTN_900 in TITANS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)