"""Effect for DINO_411 in THE_LOST_CITY"""

def battlecry(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if '0-attack' in x.name.lower() or '0-attack' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)