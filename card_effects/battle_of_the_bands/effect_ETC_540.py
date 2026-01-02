"""Effect for ETC_540 in BATTLE_OF_THE_BANDS"""


def setup(game, source):
    def on_spell(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_type == CardType.SPELL:
            from simulator.card_loader import CardDatabase
            import random
            fire = [c.card_id for c in CardDatabase.get_collectible_cards() if 'Fire' in (c.text or "")]
            if fire: trig_src.controller.add_to_hand(create_card(random.choice(fire), game))
    game.register_trigger('on_card_played', source, on_spell)
