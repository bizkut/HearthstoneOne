"""Effect for MIS_707 in WHIZBANGS_WORKSHOP"""


def on_play(game, source, target):
    source.controller.draw(2)
    game.deal_damage(source.controller.hero, 3, source)
    source.controller.add_to_deck(create_card('MIS_707', game))
    source.controller.add_to_deck(create_card('MIS_707', game))
