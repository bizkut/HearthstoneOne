"""Effect for SC_761 in SPACE"""

def on_play(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'protoss' in x.name.lower() or 'protoss' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)