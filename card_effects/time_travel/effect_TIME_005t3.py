"""Effect for TIME_005t3 in TIME_TRAVEL"""


def battlecry(game, source, target):
    player = source.controller
    rafaams = [c.card_id for c in player.deck if c.card_id.startswith('TIME_005')]
    if rafaams:
        def on_choose(game, cid):
            card = next((c for c in game.current_player.deck if c.card_id == cid), None)
            if card: game.current_player.draw_specific_card(card)
        game.initiate_discover(player, rafaams[:3], on_choose)
