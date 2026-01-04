#!/usr/bin/env python3
"""
MCTS Self-Play Data Generator.

Generates training data using Monte Carlo Tree Search with the CardTransformer model.
Optimized for Phase 9 Reinforcement Learning.
"""

import sys
import os
import argparse
import time
import json
import torch
import numpy as np
import multiprocessing as mp
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.transformer_model import CardTransformer, SequenceEncoder
from ai.mcts import MCTS
from ai.game_wrapper import HearthstoneGame
from ai.actions import Action

def _worker_fn(worker_args):
    """Worker process for parallel generation."""
    worker_id, num_games, mcts_sims, model_state, vocab, output_queue = worker_args
    
    # Initialize model in worker process
    model = CardTransformer(
        num_cards=len(vocab) + 2,
        action_dim=200,
        hidden_dim=128
    )
    if model_state:
        model.load_state_dict(model_state)
    model.eval()
    
    encoder = SequenceEncoder(vocab)
    
    # Generate games
    samples = []
    wins = 0
    
    for i in range(num_games):
        env = HearthstoneGame()
        # Randomize start player and usage of meta decks
        env.reset(randomize_first=True, use_meta_decks=True, do_mulligan=True)
        
        trajectory = [] # (state_enc, mcts_probs, player_id)
        step_count = 0
        max_steps = 100
        
        while not env.is_game_over and step_count < max_steps:
            # Clone state for MCTS root
            # Note: MCTS expects the 'Game' object (simulator) currently
            root_state = env.game.clone()
            
            # Run MCTS
            mcts = MCTS(model, encoder, root_state, num_simulations=mcts_sims)
            probs = mcts.search(root_state)
            
            # Store data
            encoded_state = encoder.encode(env.get_state())
            # Map player entity to ID 1 or 2
            pid = 1 if env.current_player == env.game.players[0] else 2
            
            trajectory.append((encoded_state, probs, pid))
            
            # Sample action (exploration during self-play)
            # Temperature annealing could go here (e.g. forced random early on)
            action_idx = np.random.choice(len(probs), p=probs)
            
            # Execute
            action_obj = Action.from_index(action_idx)
            # Apply to real env
            env.step(action_obj)
            
            step_count += 1
            
        # Outcome
        winner_id = 0
        if env.game.winner:
            winner_id = 1 if env.game.winner == env.game.players[0] else 2
            if winner_id != 0: wins += 1
            
        # Process trajectory into samples
        for (c_ids, c_feats, mask), probs, pid in trajectory:
            encoded_val = 0.0
            if winner_id == pid:
                encoded_val = 1.0
            elif winner_id != 0:
                encoded_val = -1.0
            
            # Convert MCTS probs (soft targets) to hard label for current trainer compatibility
            # In Phase 9 RL, we should save 'probs' directly. 
            # For now, we sample an action from the policy (or take argmax) as the target.
            # Ideally, we save the full probability distribution.
            # But ReplayDataset expects 'action_label' (int).
            # We'll use the sampled action index that MCTS recommended (argmax for stability of target?)
            # AlphaZero uses the prob vector.
            # For compatibility, let's use Argmax of MCTS policy.
            best_action = int(np.argmax(probs))
            
            samples.append({
                'card_ids': c_ids.tolist(),
                'card_features': c_feats.tolist(),
                'action_label': best_action,
                'game_outcome': encoded_val,
                'mcts_prob': probs.tolist() # Save RAW probs for future use
            })
            
        if (i + 1) % 10 == 0:
            # Report progress via queue if needed, or simple print
            pass
            
    output_queue.put(samples)
    return wins

def main():
    parser = argparse.ArgumentParser(description="Generate MCTS Self-Play Data")
    parser.add_argument('--sims', type=int, default=50, help='MCTS Simulations per move')
    parser.add_argument('--games', type=int, default=1000, help='Total games to generate')
    parser.add_argument('--workers', type=int, default=min(8, mp.cpu_count()), help='Parallel workers')
    parser.add_argument('--output', type=str, default='data/mcts_data.json', help='Output file')
    parser.add_argument('--vocab', type=str, default='data/vocab.json', help='Vocabulary file')
    parser.add_argument('--model', type=str, default='', help='Model checkpoint (optional)')
    
    args = parser.parse_args()
    
    print(f"Starting MCTS Generation: {args.games} games, {args.sims} sims/move, {args.workers} workers")
    
    # Load constraints
    vocab = {}
    if os.path.exists(args.vocab):
        with open(args.vocab) as f:
            vocab = json.load(f)
            # Ensure keys are ints (json dict keys are strings)
            vocab = {str(k): v for k, v in vocab.items()}
    else:
        print("Warning: Vocab not found, using empty. Model dimensions might vary.")
    
    # Load Model State
    model_state = None
    if args.model and os.path.exists(args.model):
        print(f"Loading model from {args.model}")
        model_state = torch.load(args.model, map_location='cpu')
        
    # Queue for results
    q = mp.Queue()
    
    # Split games among workers
    games_per_worker = args.games // args.workers
    worker_args = []
    for i in range(args.workers):
        count = games_per_worker + (1 if i < args.games % args.workers else 0)
        worker_args.append((i, count, args.sims, model_state, vocab, q))
        
    processes = []
    for w_args in worker_args:
        p = mp.Process(target=_worker_fn, args=(w_args,))
        p.start()
        processes.append(p)
        
    # Collect results
    all_samples = []
    finished_workers = 0
    
    while finished_workers < args.workers:
        try:
            samples = q.get()
            all_samples.extend(samples)
            finished_workers += 1
            print(f"Worker finished. Total samples collected: {len(all_samples)}")
        except:
            break
            
    for p in processes:
        p.join()
        
    # Save
    print(f"Saving {len(all_samples)} samples to {args.output}")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    with open(args.output, 'w') as f:
        json.dump({'samples': all_samples}, f)
        
    print("Done.")

if __name__ == "__main__":
    # Mac multiprocessing fix
    mp.set_start_method('spawn', force=True)
    main()
