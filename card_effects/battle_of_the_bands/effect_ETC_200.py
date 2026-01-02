"""Effect for ETC_200 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'rush' in x.name.lower() or 'rush' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)