"""Effect for ETC_532 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    player = source.controller
    # Get last 3 unique spells played
    played = []
    for cid in reversed(player.spells_played_this_game):
        if cid not in played: played.append(cid)
        if len(played) >= 3: break
    def on_choose(game, card_id):
        game.current_player.add_to_hand(create_card(card_id, game))
    game.initiate_discover(player, played, on_choose)