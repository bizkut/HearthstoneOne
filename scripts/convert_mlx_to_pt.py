"""
Convert MLX trained weights (.npz) back to PyTorch model (.pt).
Enables using the M4-optimized model within the standard HearthstoneOne game engine.
"""

import argparse
import torch
import mlx.core as mx
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.transformer_model import CardTransformer as TorchTransformer

def convert_mlx_to_pytorch(mlx_path, pt_path, large=False):
    print(f"Loading MLX weights from {mlx_path}...")
    # Load MLX weights (returns dict of arrays)
    # MLX saves as flat dictionary with dot notation names usually, or hierarchical?
    # model.save_weights saves flat dict.
    mlx_weights = mx.load(mlx_path)
    
    print("Initializing PyTorch model...")
    if large:
        pt_model = TorchTransformer(hidden_dim=256, num_layers=6, num_heads=8, dropout=0.2)
    else:
        pt_model = TorchTransformer(hidden_dim=128, num_layers=4, num_heads=4)
    
    pt_state = pt_model.state_dict()
    new_state = {}
    
    print("Converting weights...")
    
    # Mapping rules
    # MLX Linear: weight (out, in), bias (out)
    # PyTorch Linear: weight (out, in), bias (out)
    # Shapes usually match for Linear.
    # MLX Embedding: weight (num, dim) - same as PyTorch
    # LayerNorm: weight, bias - same
    
    # Key mapping might be needed if naming differs slightly.
    # Our MLX model structure mirrors PyTorch exactly in class definition,
    # so names should match mostly.
    
    matched = 0
    skipped = 0
    
    for key, val in mlx_weights.items():
        # MLX arrays to Numpy to Torch
        val_np = np.array(val)
        val_pt = torch.from_numpy(val_np)
        
        # Check for key name mismatches
        pt_key = key
        
        if pt_key not in pt_state:
            # Try to fix common naming divergences if any
            # e.g. "layers.0" vs "layers.0"
            pass
            
        if pt_key in pt_state:
            # Check shape compatibility
            if pt_state[pt_key].shape != val_pt.shape:
                # Transpose check? 
                # MLX Linear weights are (out, in) usually? 
                # Let's verify. MLX nn.Linear weight is (out, in) in recent versions?
                # Actually MLX nn.Linear weight is (input_dims, output_dims) by default!
                # PyTorch nn.Linear weight is (out_features, in_features).
                # So we MUST transpose Linear weights.
                
                if len(val_pt.shape) == 2 and val_pt.shape[::-1] == pt_state[pt_key].shape:
                    print(f"  Transposing {key} {val_pt.shape} -> {pt_state[pt_key].shape}")
                    val_pt = val_pt.T
                else:
                    print(f"  WARNING: Shape mismatch for {key}: MLX {val_pt.shape} vs PT {pt_state[pt_key].shape}")
                    skipped += 1
                    continue
            
            new_state[pt_key] = val_pt
            matched += 1
        else:
            print(f"  WARNING: Key {key} not found in PyTorch model")
            skipped += 1

    print(f"Matched {matched} layers. Skipped {skipped}.")
    
    # Load into PyTorch model
    pt_model.load_state_dict(new_state, strict=(skipped == 0))
    
    # Save
    os.makedirs(os.path.dirname(pt_path) or '.', exist_ok=True)
    torch.save(pt_model.state_dict(), pt_path)
    print(f"Successfully saved PyTorch model to {pt_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mlx", type=str, required=True, help="Input .npz file")
    parser.add_argument("--pt", type=str, required=True, help="Output .pt file")
    parser.add_argument("--large", action='store_true', help="Use large model config")
    
    args = parser.parse_args()
    convert_mlx_to_pytorch(args.mlx, args.pt, args.large)
