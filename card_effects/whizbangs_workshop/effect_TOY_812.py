"""Effect for TOY_812 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)