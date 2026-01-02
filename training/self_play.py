import os
import sys
import time
import random
import logging

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_wrapper import HearthstoneGame
from simulator.deck_generator import DeckGenerator
from simulator.enums import GamePhase

# Load Custom Zilliax cards
from scripts.implement_zilliax_custom import patch_database_for_zilliax
patch_database_for_zilliax()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RandomAgent:
    def __init__(self, name):
        self.name = name
    
    def select_action(self, valid_actions):
        if not valid_actions:
            return None
        return random.choice(valid_actions)

def run_self_play(num_games=3):
    logger.info(f"Starting Self-Play for {num_games} games...")
    
    wins = {"Player1": 0, "Player2": 0, "Draw": 0}
    
    agent1 = RandomAgent("Agent1")
    agent2 = RandomAgent("Agent2")
    
    env = HearthstoneGame()
    
    matchups = [
        ("AGGRO_ROGUE", "PEDDLER_DH", "HERO_03", "HERO_10"),
        ("PEDDLER_DH", "CONTROL_DK", "HERO_10", "HERO_11"), # HERO_11 DK placeholder
        ("CONTROL_DK", "AGGRO_ROGUE", "HERO_11", "HERO_03")
    ]
    
    start_time = time.time()
    
    for i in range(num_games):
        # Select matchup cyclicly
        deck1_name, deck2_name, h1_name, h2_name = matchups[i % len(matchups)]
        logger.info(f"Game {i+1}: {deck1_name} vs {deck2_name}")
        
        deck1 = DeckGenerator.get_preset_deck(deck1_name)
        deck2 = DeckGenerator.get_preset_deck(deck2_name)
        
        # Reset environment
        state = env.reset(deck1=deck1, deck2=deck2, hero1=h1_name, hero2=h2_name)
        
        step_count = 0
        game_over = False
        
        while not game_over:
            step_count += 1
            
            # DIRECT ACCESS TO SIMULATOR FOR THIS PHASE 0 SCRIPT
            player = env.game.current_player
            valid_actions = []
            
            # 1. End Turn (Always valid)
            valid_actions.append("END_TURN")
            
            # 2. Play Cards
            for idx, card in enumerate(player.hand):
                if player.can_play_card(card):
                    valid_actions.append(("PLAY", idx))
            
            # 3. Attacks
            for attacker in player.board:
                if attacker.can_attack():
                    targets = player.get_valid_attack_targets(attacker)
                    for target in targets:
                        valid_actions.append(("ATTACK", attacker, target))
            
            # 4. Hero Power
            if player.hero_power and player.hero_power.can_use():
                valid_actions.append("HERO_POWER")
                
            # Random choice
            if not valid_actions:
                 # Should at least have END_TURN, but just in case
                 env.game.end_turn()
                 continue
                 
            action = random.choice(valid_actions)
            
            # Apply Action
            try:
                if action == "END_TURN":
                    env.game.end_turn()
                elif action == "HERO_POWER":
                    env.game.use_hero_power()
                elif isinstance(action, tuple):
                    if action[0] == "PLAY":
                        # Simple play, random target if needed
                        if action[1] < len(player.hand):
                            card = player.hand[action[1]]
                            target = None
                            # Basic target selection logic
                            potential_targets = []
                            if env.game.get_opponent(player).hero:
                                potential_targets.append(env.game.get_opponent(player).hero)
                            potential_targets.extend(env.game.get_opponent(player).board)
                            potential_targets.extend(player.board)
                            
                            if potential_targets:
                                target = random.choice(potential_targets)
                            
                            env.game.play_card(card, target=target)
                    elif action[0] == "ATTACK":
                        env.game.attack(action[1], action[2])
            except Exception as e:
                # logger.error(f"Error executing action {action}: {e}") # Reduce spam
                env.game.end_turn() # Recovery
            
            # Check game over
            if env.game.ended:
                game_over = True
            
            # Failsafe for stuck games
            if step_count > 300:
                logger.warning(f"Game {i+1} reached step limit. Drawing.")
                game_over = True
                env.game._end_game_draw()
                
        # Result
        if env.game.players[0].play_state.name == "WON":
            wins["Player1"] += 1
            winner_deck = deck1_name
        elif env.game.players[1].play_state.name == "WON":
            wins["Player2"] += 1
            winner_deck = deck2_name
        else:
            wins["Draw"] += 1
            winner_deck = "Draw"
            
        logger.info(f"Game {i+1} finished. Winner: {winner_deck}. Steps: {step_count}")

    end_time = time.time()
    duration = end_time - start_time
    
    print("\n--- Self-Play Results ---")
    print(f"Total Games: {num_games}")
    print(f"Time Taken: {duration:.2f}s ({duration/num_games:.2f}s/game)")
    print(f"Player 1 Wins: {wins['Player1']}")
    print(f"Player 2 Wins: {wins['Player2']}")
    print(f"Draws: {wins['Draw']}")

if __name__ == "__main__":
    run_self_play(100)
