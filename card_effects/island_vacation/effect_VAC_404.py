"""Effect for VAC_404 in ISLAND_VACATION"""


def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)
    game.deal_damage(source.controller.hero, 2, source)
