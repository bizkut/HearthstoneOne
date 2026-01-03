from simulator.enums import CardType
"""Effect for ETC_521 in BATTLE_OF_THE_BANDS"""


def setup(game, source):
    def on_spell(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_type == CardType.SPELL:
            # Stats equal to cost. We use a generic token or create one.
            game.summon_token(trig_src.controller, 'ETC_521t', trig_src.zone_position + 1)
            # Would need to set its stats... simplified for now.
    game.register_trigger('on_card_played', source, on_spell)
