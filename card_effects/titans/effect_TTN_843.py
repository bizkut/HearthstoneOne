"""Effect for TTN_843 in TITANS"""


def setup(game, source):
    def on_draw(game, trig_src, card):
        if card.controller == trig_src.controller:
            game.summon_token(trig_src.controller, 'TTN_841t', 0)
    game.register_trigger('on_card_drawn', source, on_draw)
