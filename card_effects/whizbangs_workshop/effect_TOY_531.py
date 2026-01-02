"""Effect for TOY_531 in WHIZBANGS_WORKSHOP"""

def setup(game, source):
    def on_play(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_type == CardType.SPELL:
            # Effect placeholder
            pass
    game.register_trigger('on_card_played', source, on_play)