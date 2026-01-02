"""Effect for REV_310 in REVENDRETH"""

def battlecry(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range(1):
        card = next((x for x in player.deck if 'deathrattle' in x.name.lower() or 'deathrattle' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)