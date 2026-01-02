"""Effect for TOY_882 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'divine_shield' in x.name.lower() or 'divine_shield' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)