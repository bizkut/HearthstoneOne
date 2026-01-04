"""
Convert local HearthstoneOne JSON data to Hugging Face Dataset and push to Hub.
Uses generators to handle large files (4GB+) without RAM issues.
"""

import argparse
import ijson
import os
from datasets import Dataset, Features, Sequence, Value, Array2D

def generate_examples(filepath):
    """Yields examples from the massive JSON file one by one."""
    print(f"Scanning {filepath}...")
    
    # Auto-detect structure
    has_samples_key = False
    with open(filepath, 'rb') as f:
        chunk = f.read(2048)
        if b'"samples":' in chunk:
            has_samples_key = True
            
    prefix = "samples.item" if has_samples_key else "item"
    
    with open(filepath, 'rb') as f:
        # Use ijson to stream items
        for item in ijson.items(f, prefix):
            # Validate/Fix shapes if necessary
            # Ensure card_features is 2D list
            feats = item.get('card_features', [])
            
            yield {
                "card_ids": item.get('card_ids', []),
                "card_features": feats,
                "action_label": item.get('action_label', 0),
                "game_outcome": item.get('game_outcome', 0.0)
            }

def push_to_hub(input_file, repo_id, token=None):
    print(f"Preparing to push {input_file} to {repo_id}...")
    
    # Define features explicitly to ensure correct types
    features = Features({
        "card_ids": Sequence(Value("int32")),
        "card_features": Sequence(Sequence(Value("float32"))), # 2D array
        "action_label": Value("int32"),
        "game_outcome": Value("float32")
    })
    
    # Create dataset from generator
    # This doesn't load everything; it streams it during the push
    ds = Dataset.from_generator(
        generator=lambda: generate_examples(input_file),
        features=features,
    )
    
    print("Pushing to Hub (this will upload compressed chunks)...")
    ds.push_to_hub(repo_id, token=token)
    print(f"Success! Dataset available at https://huggingface.co/datasets/{repo_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Path to self_play_data.json")
    parser.add_argument("--repo", type=str, required=True, help="HF Repo ID (e.g., 'username/hearthstone-replay-v1')")
    parser.add_argument("--token", type=str, default=None, help="HF Write Token (optional if logged in via CLI)")
    
    args = parser.parse_args()
    
    push_to_hub(args.input, args.repo, args.token)
