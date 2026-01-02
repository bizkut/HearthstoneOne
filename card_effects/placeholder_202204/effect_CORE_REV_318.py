"""Effect for CORE_REV_318 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'nature' in x.name.lower() or 'nature' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)