"""
Convert HearthstoneOne JSON datasets to NumPy Memory Maps (.npy) for disk-based training.
Allows training on datasets larger than RAM (e.g., 50GB+) by mapping files directly from SSD.
"""

import os
import sys
import numpy as np
import json
import argparse
import ijson
import time

def convert_to_memmap(input_path, output_dir, seq_len=24):
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Scanning {input_path} to count samples...")
    num_samples = 0
    has_samples_key = False
    
    # Check for 'samples' key
    with open(input_path, 'rb') as f:
        chunk = f.read(2048)
        if b'"samples":' in chunk:
            has_samples_key = True
    
    prefix = "samples.item" if has_samples_key else "item"
    
    # Count samples
    with open(input_path, 'rb') as f:
        for _ in ijson.items(f, prefix):
            num_samples += 1
            if num_samples % 100000 == 0:
                sys.stdout.write(f"\r  Counted {num_samples}...")
                sys.stdout.flush()
    print(f"\nTotal samples: {num_samples}")
    
    # Define file paths
    path_ids = os.path.join(output_dir, "card_ids.npy")
    path_feats = os.path.join(output_dir, "card_features.npy")
    path_lbls = os.path.join(output_dir, "labels.npy")
    path_outs = os.path.join(output_dir, "outcomes.npy")
    path_meta = os.path.join(output_dir, "metadata.json")
    
    # Create Memmaps (Write mode)
    print("Allocating disk space...")
    mm_ids = np.memmap(path_ids, dtype='int32', mode='w+', shape=(num_samples, seq_len))
    mm_feats = np.memmap(path_feats, dtype='float32', mode='w+', shape=(num_samples, seq_len, 11))
    mm_lbls = np.memmap(path_lbls, dtype='int32', mode='w+', shape=(num_samples,))
    mm_outs = np.memmap(path_outs, dtype='float32', mode='w+', shape=(num_samples, 1))
    
    print("Streaming data to disk (this may take a while)...")
    start_time = time.time()
    
    with open(input_path, 'rb') as f:
        idx = 0
        for s in ijson.items(f, prefix):
            # Card IDs
            c_ids = s.get('card_ids', [])
            ln = min(len(c_ids), seq_len)
            if ln > 0:
                mm_ids[idx, :ln] = c_ids[:ln]
            
            # Card Features
            c_feats = s.get('card_features', [])
            # Only convert if not empty
            if c_feats:
                feat_arr = np.array(c_feats, dtype=np.float32)
                ln = min(feat_arr.shape[0], seq_len)
                if ln > 0:
                    mm_feats[idx, :ln] = feat_arr[:ln]
            
            # Labels & Outcomes
            mm_lbls[idx] = s.get('action_label', 0)
            mm_outs[idx] = s.get('game_outcome', 0.0)
            
            idx += 1
            if idx % 10000 == 0:
                elapsed = time.time() - start_time
                rate = idx / elapsed
                sys.stdout.write(f"\r  Processed {idx}/{num_samples} ({rate:.1f} samples/s)")
                sys.stdout.flush()
    
    # Flush to disk
    mm_ids.flush()
    mm_feats.flush()
    mm_lbls.flush()
    mm_outs.flush()
    
    # Save metadata
    meta = {
        'num_samples': num_samples,
        'seq_len': seq_len,
        'feature_dim': 11,
        'shapes': {
            'card_ids': [num_samples, seq_len],
            'card_features': [num_samples, seq_len, 11],
            'labels': [num_samples],
            'outcomes': [num_samples, 1]
        }
    }
    with open(path_meta, 'w') as f:
        json.dump(meta, f, indent=2)
        
    print(f"\n\nConversion complete!")
    print(f"Data saved to: {output_dir}")
    print(f"Use this directory as --data argument for training.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert JSON dataset to Binary Memmap")
    parser.add_argument('--input', type=str, required=True, help="Input JSON file")
    parser.add_argument('--output', type=str, required=True, help="Output directory for binary files")
    
    args = parser.parse_args()
    convert_to_memmap(args.input, args.output)
