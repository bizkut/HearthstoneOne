"""Effect for VAC_333 in ISLAND_VACATION"""


def battlecry(game, source, target):
    # Replay last card from another class
    history = [c for c in source.controller.cards_played_this_game if c.card_class != source.controller.hero.data.card_class]
    if history:
        game.play_card(create_card(history[-1], game))
