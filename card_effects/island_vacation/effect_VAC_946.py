"""Effect for VAC_946 in ISLAND_VACATION"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)