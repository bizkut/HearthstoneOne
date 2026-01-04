#!/usr/bin/env python3
"""
Convert self-play data to text prompts for Gemma LLM fine-tuning.

Converts card_ids and action_labels to human-readable text prompts
suitable for language model training.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Slot layout in the data:
# [0-6]   = My Board (7 slots)
# [7-16]  = My Hand (10 slots)
# [17-23] = Enemy Board (7 slots)
MY_BOARD_START, MY_BOARD_END = 0, 7
MY_HAND_START, MY_HAND_END = 7, 17
ENEMY_BOARD_START, ENEMY_BOARD_END = 17, 24


def action_label_to_text(action_label: int, hand_cards: List[str], board_cards: List[str]) -> str:
    """
    Convert action index to human-readable text.
    
    Action space layout:
    - 0-9: Play card from hand (index 0-9)
    - 10: Use Hero Power
    - 11-17: Attack with minion (board index 0-6)
    - 18: Attack with hero
    """
    if 0 <= action_label <= 9:
        # Play card from hand
        card_idx = action_label
        if card_idx < len(hand_cards) and hand_cards[card_idx]:
            return f"PLAY {hand_cards[card_idx]}"
        return f"PLAY hand_slot_{card_idx}"
    
    elif action_label == 10:
        return "USE HERO POWER"
    
    elif 11 <= action_label <= 17:
        # Attack with minion
        minion_idx = action_label - 11
        if minion_idx < len(board_cards) and board_cards[minion_idx]:
            return f"ATTACK with {board_cards[minion_idx]}"
        return f"ATTACK with minion_{minion_idx}"
    
    elif action_label == 18:
        return "ATTACK with Hero"
    
    return "END TURN"


class PromptConverter:
    """Converts self-play data to Gemma training prompts."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.vocab_reverse: Dict[int, str] = {}  # idx -> card_id
        self.card_names: Dict[str, str] = {}     # card_id -> name
        
    def load(self) -> bool:
        """Load vocabulary and card database."""
        # Load vocab (card_id -> idx)
        vocab_path = self.data_dir / "vocab.json"
        if not vocab_path.exists():
            print(f"Vocab not found at {vocab_path}")
            return False
            
        with open(vocab_path) as f:
            vocab = json.load(f)
        
        # Reverse: idx -> card_id
        self.vocab_reverse = {v: k for k, v in vocab.items()}
        print(f"Loaded {len(self.vocab_reverse)} vocab entries")
        
        # Load card database for names
        cards_path = self.data_dir / "cards.collectible.json"
        if cards_path.exists():
            with open(cards_path) as f:
                cards = json.load(f)
            self.card_names = {c['id']: c['name'] for c in cards if 'id' in c and 'name' in c}
            print(f"Loaded {len(self.card_names)} card names")
        
        # Also load non-collectible cards
        cards_all_path = self.data_dir / "cards.json"
        if cards_all_path.exists():
            with open(cards_all_path) as f:
                cards_all = json.load(f)
            for c in cards_all:
                if 'id' in c and 'name' in c and c['id'] not in self.card_names:
                    self.card_names[c['id']] = c['name']
            print(f"Total card names: {len(self.card_names)}")
        
        return True
    
    def get_card_name(self, card_id: str) -> str:
        """Get human-readable card name."""
        return self.card_names.get(card_id, card_id)
    
    def idx_to_name(self, idx: int) -> str:
        """Convert vocab index to card name."""
        if idx == 0:
            return ""  # PAD token
        if idx == 1:
            return "Unknown"  # UNKNOWN token
        
        card_id = self.vocab_reverse.get(idx, f"ID_{idx}")
        return self.get_card_name(card_id)
    
    def format_features(self, features: List[float]) -> str:
        """Format card features as text (cost/attack/health)."""
        # Features layout: [cost_norm, atk_norm, hp_norm, is_minion, is_spell, ...]
        # Normalized by /10 or /12, so reverse it
        if len(features) < 3:
            return ""
        
        cost = int(features[0] * 10)
        attack = int(features[1] * 12)
        health = int(features[2] * 12)
        
        if attack > 0 or health > 0:
            return f"({cost}/{attack}/{health})"
        elif cost > 0:
            return f"({cost})"
        return ""
    
    def sample_to_prompt(self, sample: Dict[str, Any]) -> str:
        """Convert a single sample to a text prompt."""
        card_ids = sample['card_ids']
        card_features = sample['card_features']
        action_label = sample['action_label']
        
        # Parse slots
        my_board = []
        for i in range(MY_BOARD_START, MY_BOARD_END):
            if card_ids[i] > 0:
                name = self.idx_to_name(card_ids[i])
                stats = self.format_features(card_features[i])
                my_board.append(f"{name}{stats}")
        
        my_hand = []
        for i in range(MY_HAND_START, MY_HAND_END):
            if card_ids[i] > 0:
                name = self.idx_to_name(card_ids[i])
                stats = self.format_features(card_features[i])
                my_hand.append(f"{name}{stats}")
        
        enemy_board = []
        for i in range(ENEMY_BOARD_START, ENEMY_BOARD_END):
            if card_ids[i] > 0:
                name = self.idx_to_name(card_ids[i])
                stats = self.format_features(card_features[i])
                enemy_board.append(f"{name}{stats}")
        
        # Get action text
        hand_names = [self.idx_to_name(card_ids[i]) for i in range(MY_HAND_START, MY_HAND_END) if card_ids[i] > 0]
        board_names = [self.idx_to_name(card_ids[i]) for i in range(MY_BOARD_START, MY_BOARD_END) if card_ids[i] > 0]
        action_text = action_label_to_text(action_label, hand_names, board_names)
        
        # Build prompt
        lines = ["Game State:"]
        
        if my_board:
            lines.append(f"My Board: {', '.join(my_board)}")
        else:
            lines.append("My Board: empty")
            
        if my_hand:
            lines.append(f"My Hand: {', '.join(my_hand)}")
        else:
            lines.append("My Hand: empty")
            
        if enemy_board:
            lines.append(f"Enemy Board: {', '.join(enemy_board)}")
        else:
            lines.append("Enemy Board: empty")
        
        lines.append("")
        lines.append(f"Best Action: {action_text}")
        
        return "\n".join(lines)
    
    def convert(self, input_path: str, output_path: str, limit: int = None):
        """Convert input JSON to output JSONL for training."""
        print(f"Loading data from {input_path}...")
        
        # Check file size to decide on streaming
        file_size_gb = os.path.getsize(input_path) / (1024**3)
        use_streaming = file_size_gb > 0.5  # Use streaming for files > 500MB
        
        if use_streaming:
            print(f"Large file detected ({file_size_gb:.1f}GB) - using streaming parser...")
            self._convert_streaming(input_path, output_path, limit)
        else:
            self._convert_standard(input_path, output_path, limit)
    
    def _convert_standard(self, input_path: str, output_path: str, limit: int = None):
        """Standard conversion for smaller files (loads into memory)."""
        with open(input_path) as f:
            data = json.load(f)
        
        samples = data.get('samples', data if isinstance(data, list) else [])
        total = len(samples)
        
        if limit:
            samples = samples[:limit]
            print(f"Processing {len(samples)} of {total} samples (limited)")
        else:
            print(f"Processing all {total} samples")
        
        self._write_samples(samples, output_path, total)
    
    def _convert_streaming(self, input_path: str, output_path: str, limit: int = None):
        """Streaming conversion for large files (2.7M+ samples)."""
        try:
            import ijson
        except ImportError:
            print("Installing ijson for streaming JSON parsing...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "ijson", "-q"])
            import ijson
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        count = 0
        with open(input_path, 'rb') as f_in, open(output_path, 'w') as f_out:
            # Stream samples from JSON
            samples = ijson.items(f_in, 'samples.item')
            
            for sample in samples:
                if limit and count >= limit:
                    break
                
                prompt_text = self.sample_to_prompt(sample)
                entry = {"text": f"<bos>{prompt_text}<eos>"}
                f_out.write(json.dumps(entry) + "\n")
                
                count += 1
                if count % 100000 == 0:
                    print(f"Converted {count:,} samples...")
        
        print(f"Saved {count:,} prompts to {output_path}")
        
        # Print sample
        if count > 0:
            # Re-read first sample for preview
            with open(input_path, 'rb') as f:
                first_sample = next(ijson.items(f, 'samples.item'))
                print("\n--- Sample Prompt ---")
                print(self.sample_to_prompt(first_sample))
                print("---------------------\n")
    
    def _write_samples(self, samples, output_path: str, total: int):
        """Write samples to output file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            count = 0
            for sample in samples:
                prompt_text = self.sample_to_prompt(sample)
                entry = {"text": f"<bos>{prompt_text}<eos>"}
                f.write(json.dumps(entry) + "\n")
                
                count += 1
                if count % 10000 == 0:
                    print(f"Converted {count:,}/{len(samples):,} samples...")
        
        print(f"Saved {len(samples):,} prompts to {output_path}")
        
        # Print sample
        if samples:
            print("\n--- Sample Prompt ---")
            print(self.sample_to_prompt(samples[0]))
            print("---------------------\n")


def main():
    parser = argparse.ArgumentParser(description='Convert self-play data to Gemma prompts')
    parser.add_argument('--input', type=str, default='data/self_play_data.json',
                        help='Input JSON file')
    parser.add_argument('--output', type=str, default='data/gemma_train.jsonl',
                        help='Output JSONL file')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Data directory (for vocab, cards)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of samples (for testing)')
    
    args = parser.parse_args()
    
    converter = PromptConverter(args.data_dir)
    if not converter.load():
        sys.exit(1)
    
    converter.convert(args.input, args.output, args.limit)


if __name__ == '__main__':
    main()
