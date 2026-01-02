"""Effect for TOY_880 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)