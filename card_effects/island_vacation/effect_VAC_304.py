"""Effect for VAC_304 in ISLAND_VACATION"""


def battlecry(game, source, target):
    # Discovery of cast spells while holding - simplified to just last 3 spells
    options = source.controller.spells_played_this_game[-3:]
    if options:
        def on_choose(game, cid):
            game.current_player.add_to_hand(create_card(cid, game))
        game.initiate_discover(source.controller, options, on_choose)
