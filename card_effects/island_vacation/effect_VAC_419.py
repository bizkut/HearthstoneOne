"""Effect for VAC_419 in ISLAND_VACATION"""


def on_play(game, source, target):
    for p in game.players:
        game.deal_damage(p.hero, 4, source)
