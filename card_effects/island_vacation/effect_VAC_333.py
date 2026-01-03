"""Effect for VAC_333 in ISLAND_VACATION"""
from simulator.card_loader import CardDatabase, create_card

def battlecry(game, source, target):
    # Replay last card from another class
    history = []
    player_class = source.controller.hero.data.card_class if source.controller.hero else None
    
    for cid in source.controller.cards_played_this_game:
        data = CardDatabase.get_card(cid)
        if data and data.card_class != player_class:
            history.append(cid)
            
    if history:
        new_card = create_card(history[-1], game)
        if new_card:
            game.play_card(new_card)
