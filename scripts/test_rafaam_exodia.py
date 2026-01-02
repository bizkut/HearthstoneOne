import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator.game import Game
from simulator.player import Player
from simulator.card_loader import CardDatabase, create_card
from simulator.enums import GamePhase, Step

def test_rafaam_exodia():
    print("--- Initialisation du test Rafaam Exodia ---")
    db = CardDatabase.load()
    
    # Création des joueurs avec des decks contenant Rafaam
    p1 = Player("Joueur 1")
    p2 = Player("Joueur 2")
    
    game = Game()
    # Hero setup
    p1.hero = create_card("HERO_07", game) # Warlock (Gul'dan)
    p1.hero.controller = p1
    p2.hero = create_card("HERO_01", game) # Warrior (Garrosh)
    p2.hero.controller = p2
    
    game.setup(p1, p2)
    # Force Joueur 1 à être le premier joueur pour le test
    game.players = [p1, p2]
    game.current_player_idx = 0
    p1.opponent = p2
    p2.opponent = p1
    
    game.phase = GamePhase.MAIN_ACTION
    game.step = Step.MAIN_ACTION
    
    # On force Rafaam et ses versions en main du Joueur 1
    rafaams = [
        'TIME_005', 'TIME_005t1', 'TIME_005t2', 'TIME_005t3', 
        'TIME_005t4', 'TIME_005t5', 'TIME_005t6', 
        'TIME_005t7', 'TIME_005t8', 'TIME_005t9'
    ]
    
    print(f"Préparation de la main de {p1.name}...")
    p1.hand = [] # Clear hand to make space (remove coin/mulligan cards)
    for rid in rafaams:
        p1.add_to_hand(create_card(rid, game))
    
    print(f"Main de {p1.name} ({len(p1.hand)} cartes): {[c.card_id for c in p1.hand]}")
    p1.mana = 10
    
    # Simuler le jeu des 9 premiers Rafaams
    print("\n--- Phase 1: Jeu des 9 variantes de Rafaam ---")
    for rid in rafaams[1:]:
        card = next((c for c in p1.hand if c.card_id == rid), None)
        if card:
            print(f"Jouant {card.name} ({card.card_id})...")
            p1.mana = 10 # Reset mana for each play
            success = game.play_card(card)
            if not success:
                print(f"ECHEC du jeu de {card.name}")
            # Vider le board pour ne pas bloquer
            p1.board = []
    
    print("\n--- Phase 2: Jeu du Timethief Rafaam final ---")
    p1.mana = 10
    final_rafaam = next((c for c in p1.hand if c.card_id == 'TIME_005'), None)
    
    print(f"PV adversaire avant: {p2.hero.health}")
    game.play_card(final_rafaam)
    print(f"PV adversaire apres: {p2.hero.health}")
    
    if p2.hero.health <= 0:
        print("\nSUCCESS : Rafaam Exodia a detruit le heros adverse !")
    else:
        print("\nFAILURE : Le heros adverse est encore en vie.")
        print(f"Rafaams joues: {getattr(p1, 'rafaams_played', 'AUCUN')}")

if __name__ == "__main__":
    test_rafaam_exodia()
