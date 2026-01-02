"""Effect for ETC_074 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    player = source.controller
    options = list(set(source.controller.opponent.cards_played_this_game))
    if options:
        import random
        chosen = random.sample(options, min(3, len(options)))
        def on_choose(game, cid):
            game.current_player.add_to_hand(create_card(cid, game))
        game.initiate_discover(player, chosen, on_choose)
