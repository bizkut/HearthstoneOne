"""Effect for TIME_609 in TIME_TRAVEL"""
from simulator.card_loader import CardDatabase

def battlecry(game, source, target):
    # Deal 2 damage to all enemies, repeat logic simplified
    repeats = 1
    # Check for sisters in history
    played_names = []
    for cid in source.controller.cards_played_this_game:
        data = CardDatabase.get_card(cid)
        if data:
            played_names.append(data.name)
            
    # Note: Using partial names as logic suggests 'Alleria' and 'Vereesa'
    if any('Alleria' in name for name in played_names): repeats += 1
    if any('Vereesa' in name for name in played_names): repeats += 1
    
    for _ in range(repeats):
        opponent = game.get_opponent(source.controller)
        targets = [m for m in opponent.board]
        if opponent.hero:
            targets.append(opponent.hero)
        
        for m in targets:
            game.deal_damage(m, 2, source)
