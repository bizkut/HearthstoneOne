"""Effect for TIME_013 in TIME_TRAVEL"""


def setup(game, source):
    source.elusive = True
    def on_play(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_type == CardType.SPELL:
            from simulator.card_loader import CardDatabase
            import random
            natures = [c.card_id for c in CardDatabase.get_collectible_cards() if c.spell_school == 'NATURE']
            if natures:
                game.current_player.add_to_hand(create_card(random.choice(natures), game))
    game.register_trigger('on_card_played', source, on_play)
