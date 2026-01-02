import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator.game import Game
from simulator.player import Player
from simulator.card_loader import CardDatabase, create_card
from simulator.enums import GamePhase, Step, Zone

def setup_test_game():
    p1 = Player("Joueur 1")
    p2 = Player("Joueur 2")
    game = Game()
    p1.hero = create_card("HERO_01", game) # Warrior
    p1.hero.controller = p1
    p2.hero = create_card("HERO_02", game) # Mage
    p2.hero.controller = p2
    game.setup(p1, p2)
    game.players = [p1, p2]
    game.current_player_idx = 0
    p1.opponent = p2
    p2.opponent = p1
    game.phase = GamePhase.MAIN_ACTION
    game.step = Step.MAIN_ACTION
    p1.mana = 10
    return game, p1, p2

def test_king_maluk():
    print("\n--- Test: King Maluk & Infinite Banana ---")
    game, p1, p2 = setup_test_game()
    p1.add_to_hand(create_card("CS2_182", game)) # Boulderfist Ogre
    p1.add_to_hand(create_card("TIME_042", game)) # King Maluk
    
    print(f"Main avant: {[c.name for c in p1.hand]}")
    maluk = next(c for c in p1.hand if c.card_id == "TIME_042")
    game.play_card(maluk)
    
    print(f"Main après Maluk: {[c.name for c in p1.hand]}")
    banana = next((c for c in p1.hand if c.card_id == "TIME_042t"), None)
    if banana:
        print("SUCCESS: Banane Infinie obtenue !")
        # Jouer la banane sur Maluk
        game.play_card(banana, maluk)
        print(f"Stats Maluk après banane: {maluk.attack}/{maluk.health}")
        print(f"Main après banane: {[c.name for c in p1.hand]} (devrait contenir une nouvelle banane)")
    else:
        print("FAILURE: Banane non trouvée.")

def test_murozond():
    print("\n--- Test: Murozond, Unbounded ---")
    game, p1, p2 = setup_test_game()
    murozond = create_card("TIME_024", game)
    p1.add_to_hand(murozond)
    game.play_card(murozond)
    print(f"Murozond joué. Attaque actuelle: {murozond.attack}")
    
    print("Passage au tour suivant...")
    game.end_turn() # P1 end
    game.end_turn() # P2 end -> P1 start
    
    print(f"Attaque de Murozond au début du tour: {murozond.attack}")
    if murozond.attack >= 99:
        print("SUCCESS: Murozond a atteint l'attaque INFINIE !")
    else:
        print("FAILURE: Attaque de Murozond inchangée.")

def test_hooktail():
    print("\n--- Test: Time Adm'ral Hooktail & Chest ---")
    game, p1, p2 = setup_test_game()
    hooktail = create_card("TIME_713", game)
    p1.add_to_hand(hooktail)
    game.play_card(hooktail)
    
    print(f"Board adverse: {[m.name for m in p2.board]}")
    chest = next((m for m in p2.board if m.card_id == "TIME_713t"), None)
    if chest:
        print(f"SUCCESS: Le coffre {chest.name} est sur le board adverse !")
        print(f"Main de P1 avant destruction: {len(p1.hand)} cartes")
        chest.destroy() # Simule la destruction du coffre
        game.process_deaths()
        print(f"Main de P1 après destruction: {len(p1.hand)} cartes (Pièces attendues)")
        if any(c.card_id == "GAME_005" for c in p1.hand):
            print("SUCCESS: 5 Pièces reçues !")
    else:
        print("FAILURE: Coffre non invoqué.")

if __name__ == "__main__":
    test_king_maluk()
    test_murozond()
    test_hooktail()
