"""Effect for TIME_063 in TIME_TRAVEL"""


def setup(game, source):
    source.dormant = 5
    source.rush = True
    def on_play(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_set == 'TIME_TRAVEL':
            trig_src.dormant = max(0, trig_src.dormant - 1)
    game.register_trigger('on_card_played', source, on_play)
