"""Effect for VAC_431 in ISLAND_VACATION"""

def on_play(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'different' in x.name.lower() or 'different' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)