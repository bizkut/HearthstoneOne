"""
Mulligan Training Script for HearthstoneOne AI.

Collects mulligan decisions during self-play and trains the MulliganPolicy.
Uses outcome-based learning: mulligan decisions are associated with game wins/losses.
"""

import sys
import os
import torch
import numpy as np
import time
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.mulligan_policy import MulliganPolicy, MulliganEncoder, MulliganExample, MulliganTrainer
from ai.game_wrapper import HearthstoneGame
from ai.model import HearthstoneModel
from training.meta_decks import get_random_deck_pair


class MulliganDataCollector:
    """Collects mulligan data from self-play games."""
    
    def __init__(self, policy: MulliganPolicy = None):
        self.policy = policy or MulliganPolicy()
        self.encoder = MulliganEncoder()
        self.examples: List[MulliganExample] = []
        
    def collect_games(self, num_games: int, use_exploration: bool = True) -> List[MulliganExample]:
        """
        Play games and collect mulligan decisions with outcomes.
        
        Args:
            num_games: Number of games to play
            use_exploration: If True, add randomness to mulligan decisions
            
        Returns:
            List of MulliganExamples
        """
        collected = []
        wins = 0
        
        print(f"Collecting mulligan data from {num_games} games...")
        
        for game_idx in range(num_games):
            env = HearthstoneGame()
            
            # Get meta decks for realistic training
            try:
                ds1, ds2 = get_random_deck_pair()
                env.reset(deckstring1=ds1, deckstring2=ds2, randomize_first=True, do_mulligan=False)
            except:
                env.reset(randomize_first=True, do_mulligan=False)
            
            # Get class indices
            p1 = env.game.players[0]
            p2 = env.game.players[1]
            p1_class = env._get_class_index(p1.hero.card_id if p1.hero else "HERO_08")
            p2_class = env._get_class_index(p2.hero.card_id if p2.hero else "HERO_01")
            
            # Record mulligan for P1
            p1_hand = list(p1.hand)
            p1_decisions = self._make_mulligan_decision(p1_hand, p2_class, p1_class, use_exploration)
            p1_example = MulliganExample(
                hand_cards=[self._card_to_dict(c) for c in p1_hand],
                opponent_class=p2_class,
                player_class=p1_class,
                cards_kept=p1_decisions
            )
            
            # Record mulligan for P2
            p2_hand = list(p2.hand)
            p2_decisions = self._make_mulligan_decision(p2_hand, p1_class, p2_class, use_exploration)
            p2_example = MulliganExample(
                hand_cards=[self._card_to_dict(c) for c in p2_hand],
                opponent_class=p1_class,
                player_class=p2_class,
                cards_kept=p2_decisions
            )
            
            # Apply mulligan decisions
            cards_to_replace = [c for i, c in enumerate(p1.hand) if i < len(p1_decisions) and not p1_decisions[i]]
            env.game.do_mulligan(p1, cards_to_replace)
            
            cards_to_replace = [c for i, c in enumerate(p2.hand) if i < len(p2_decisions) and not p2_decisions[i]]
            env.game.do_mulligan(p2, cards_to_replace)
            
            # Play out the game (simplified - just random actions)
            step_count = 0
            max_steps = 100
            
            while not env.is_game_over and step_count < max_steps:
                player = env.current_player
                
                # Simple random action: play a card or end turn
                playable = [c for c in player.hand if player.can_play_card(c)]
                
                if playable and np.random.random() > 0.3:
                    card = np.random.choice(playable)
                    try:
                        env.game.play_card(card, None)
                    except:
                        env.game.end_turn()
                else:
                    env.game.end_turn()
                
                step_count += 1
            
            # Determine winner and assign outcomes
            winner = env.game.winner
            p1_won = winner == p1
            p2_won = winner == p2
            
            p1_example.game_won = p1_won
            p2_example.game_won = p2_won
            
            collected.append(p1_example)
            collected.append(p2_example)
            
            if p1_won or p2_won:
                wins += 1
            
            if (game_idx + 1) % 10 == 0:
                print(f"  {game_idx + 1}/{num_games} games collected")
        
        self.examples.extend(collected)
        print(f"Collected {len(collected)} mulligan examples from {num_games} games")
        return collected
    
    def _make_mulligan_decision(self, hand: list, opponent_class: int, player_class: int, 
                                 use_exploration: bool) -> List[bool]:
        """Make mulligan decision with optional exploration."""
        if use_exploration and np.random.random() < 0.3:
            # Pure exploration: random decisions
            return [np.random.random() > 0.5 for _ in hand]
        else:
            # Use policy (or heuristic if untrained)
            return self.policy.get_mulligan_decision(hand, opponent_class, player_class)
    
    def _card_to_dict(self, card) -> dict:
        """Convert card to dictionary for encoding."""
        return {
            'cost': getattr(card, 'cost', 0),
            'attack': getattr(card, 'attack', 0),
            'health': getattr(card, 'health', 0),
            'card_type': getattr(card, 'card_type', 0),
        }


def train_mulligan_policy(
    num_iterations: int = 10,
    games_per_iter: int = 50,
    batch_size: int = 32,
    save_path: str = "models/mulligan_policy.pt"
):
    """
    Train mulligan policy using outcome-based learning.
    
    Args:
        num_iterations: Number of training iterations
        games_per_iter: Games to collect per iteration
        batch_size: Training batch size
        save_path: Path to save trained policy
    """
    policy = MulliganPolicy()
    trainer = MulliganTrainer(policy)
    collector = MulliganDataCollector(policy)
    
    print("=" * 50)
    print("Mulligan Policy Training")
    print("=" * 50)
    
    for iteration in range(num_iterations):
        print(f"\n--- Iteration {iteration + 1}/{num_iterations} ---")
        
        # Collect data
        examples = collector.collect_games(games_per_iter, use_exploration=True)
        
        for ex in examples:
            trainer.add_example(ex)
        
        # Train
        if len(trainer.dataset) >= batch_size:
            num_batches = len(trainer.dataset) // batch_size
            total_loss = 0.0
            
            for _ in range(num_batches):
                loss = trainer.train_batch(batch_size)
                total_loss += loss
            
            avg_loss = total_loss / max(num_batches, 1)
            print(f"Training loss: {avg_loss:.4f}")
    
    # Save
    os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
    trainer.save(save_path)
    print(f"\nMulligan policy saved to {save_path}")
    
    return policy


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Mulligan Policy')
    parser.add_argument('--iterations', type=int, default=10, help='Training iterations')
    parser.add_argument('--games', type=int, default=50, help='Games per iteration')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--output', type=str, default='models/mulligan_policy.pt',
                        help='Output path')
    
    args = parser.parse_args()
    
    train_mulligan_policy(
        num_iterations=args.iterations,
        games_per_iter=args.games,
        batch_size=args.batch_size,
        save_path=args.output
    )
