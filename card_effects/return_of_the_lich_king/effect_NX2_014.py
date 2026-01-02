"""Effect for NX2_014 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if '1-cost' in x.name.lower() or '1-cost' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)