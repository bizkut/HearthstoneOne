#!/usr/bin/env python3
"""Merge training datasets with a rolling window to prevent unbounded growth.

Usage:
    python3 scripts/merge_datasets.py --base data/combined.json --new data/rl_data.json --max-samples 100000
"""

import argparse
import json
import os
import sys


def merge_datasets(base_path: str, new_path: str, output_path: str, max_samples: int) -> None:
    """Merge datasets keeping only the most recent samples."""
    
    # Load base dataset (or create empty if doesn't exist)
    if os.path.exists(base_path):
        print(f"Loading base: {base_path}")
        with open(base_path, 'r') as f:
            base = json.load(f)
    else:
        print(f"Base file not found, starting fresh")
        base = {"samples": []}
    
    # Load new dataset
    print(f"Loading new: {new_path}")
    with open(new_path, 'r') as f:
        new = json.load(f)
    
    old_count = len(base.get("samples", []))
    new_count = len(new.get("samples", []))
    
    # Merge and apply rolling window
    combined = base.get("samples", []) + new.get("samples", [])
    combined = combined[-max_samples:]  # Keep only last N samples
    
    # Update base with merged samples
    base["samples"] = combined
    
    # Write output
    print(f"Writing: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(base, f)
    
    final_count = len(combined)
    discarded = (old_count + new_count) - final_count
    
    print(f"\nMerge complete:")
    print(f"  Base samples:     {old_count:,}")
    print(f"  New samples:      {new_count:,}")
    print(f"  Final samples:    {final_count:,}")
    if discarded > 0:
        print(f"  Discarded (old):  {discarded:,}")


def main():
    parser = argparse.ArgumentParser(description="Merge datasets with rolling window")
    parser.add_argument("--base", required=True, help="Base dataset (will be updated or created)")
    parser.add_argument("--new", required=True, help="New dataset to merge")
    parser.add_argument("--output", help="Output path (defaults to --base)")
    parser.add_argument("--max-samples", type=int, default=100000, help="Max samples to keep (default: 100000)")
    
    args = parser.parse_args()
    output = args.output or args.base
    
    merge_datasets(args.base, args.new, output, args.max_samples)


if __name__ == "__main__":
    main()
