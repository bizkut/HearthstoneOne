from simulator.enums import CardType
"""Effect for VAC_408 in ISLAND_VACATION"""


def on_play(game, source, target):
    player = source.controller
    minions = list(set([c.card_id for c in player.deck if c.card_type == CardType.MINION]))
    def on_choose(game, cid):
        card = next((c for c in game.current_player.deck if c.card_id == cid), None)
        if card: game.current_player.draw_specific_card(card)
    game.initiate_discover(player, minions, on_choose)
