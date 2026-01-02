"""Effect for FIR_929 in EMERALD_DREAM"""

def battlecry(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'fire' in x.name.lower() or 'fire' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)