"""Effect for CORE_EX1_187 in PLACEHOLDER_202204"""

def setup(game, source):
    def on_spell(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_type == CardType.SPELL:
            trig_src.attack += 2; trig_src.max_health += 2; trig_src.health += 2
    game.register_trigger('on_card_played', source, on_spell)