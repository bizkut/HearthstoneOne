"""Effect for AV_328 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'holy' in x.name.lower() or 'holy' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)