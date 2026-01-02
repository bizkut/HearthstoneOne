"""Effect for TOY_507 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'battlecry' in x.name.lower() or 'battlecry' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)