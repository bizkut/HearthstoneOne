"""Effect for TIME_209t in TIME_TRAVEL"""


def setup(game, source):
    source.windfury = True

def deathrattle(game, source):
    card = create_card('TIME_209t', game)
    # Permanent buff logic would need a state tracker, simplifying to +2 Attack
    card.attack += 2
    source.controller.add_to_deck(card)
