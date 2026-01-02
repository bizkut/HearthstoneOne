"""Effect for TTN_926 in TITANS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)