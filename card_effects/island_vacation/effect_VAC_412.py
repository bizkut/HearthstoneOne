"""Effect for VAC_412 in ISLAND_VACATION"""


def battlecry(game, source, target):
    game.summon_token(source.controller.opponent, 'VAC_412t', 0)
