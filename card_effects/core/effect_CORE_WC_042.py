"""Effect for CORE_WC_042 in CORE"""

def setup(game, source):
    def on_play_c(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_type == CardType.MINION and card.data.race == Race.ELEMENTAL:
            trig_src.attack += 1
    game.register_trigger('on_card_played', source, on_play_c)