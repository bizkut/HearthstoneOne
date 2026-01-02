"""Effect for TIME_042t in TIME_TRAVEL"""


def on_play(game, source, target):
    if target:
        target.attack += 1; target.max_health += 1; target.health += 1
    source.controller.add_to_hand(create_card('TIME_042t', game))
