"""Effect for ICC_314 in ICECROWN"""


def setup(game, source):
    source.taunt = True
    def on_end(game, trig_src):
        if game.current_player == trig_src.controller:
            import random
            dk_cards = ['ICC_314t1', 'ICC_314t2', 'ICC_314t3', 'ICC_314t4', 'ICC_314t5', 'ICC_314t6', 'ICC_314t7', 'ICC_314t8']
            trig_src.controller.add_to_hand(create_card(random.choice(dk_cards), game))
    game.register_trigger('on_turn_end', source, on_end)
