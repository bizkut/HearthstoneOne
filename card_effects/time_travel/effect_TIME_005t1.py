"""Effect for TIME_005t1 in TIME_TRAVEL"""


def battlecry(game, source, target):
    # Draw a Rafaam
    player = source.controller
    c = next((x for x in player.deck if x.card_id.startswith('TIME_005')), None)
    if c: player.draw_specific_card(c)

def deathrattle(game, source):
    # Draw a Rafaam
    player = source.controller
    c = next((x for x in player.deck if x.card_id.startswith('TIME_005')), None)
    if c: player.draw_specific_card(c)
