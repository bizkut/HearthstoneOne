"""Effect for VAC_929 in ISLAND_VACATION"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)