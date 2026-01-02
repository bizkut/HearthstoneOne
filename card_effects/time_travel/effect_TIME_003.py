"""Effect for TIME_003 in TIME_TRAVEL"""

def battlecry(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'random' in x.name.lower() or 'random' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)