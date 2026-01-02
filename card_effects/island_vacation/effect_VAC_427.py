"""Effect for VAC_427 in ISLAND_VACATION"""


def on_play(game, source, target):
    if target: game.deal_damage(target, 3, source)
