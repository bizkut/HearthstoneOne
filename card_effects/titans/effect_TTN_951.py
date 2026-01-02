"""Effect for TTN_951 in TITANS"""

def on_play(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'choose_one' in x.name.lower() or 'choose_one' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)