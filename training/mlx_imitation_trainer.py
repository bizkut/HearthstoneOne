"""
MLX Imitation Learning Trainer for HearthstoneOne AI.

Optimized for Apple Silicon (M1/M2/M3/M4).
Auto-converts JSON input to binary format and outputs PyTorch-compatible model.
"""

import os
import sys
import time
import json
import tempfile
import shutil
import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import ijson

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.mlx_transformer_model import CardTransformer


def convert_json_to_binary(input_path, output_dir, seq_len=24):
    """Convert JSON dataset to binary memmap format (inline version)."""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Converting JSON to binary format...")
    num_samples = 0
    has_samples_key = False
    
    with open(input_path, 'rb') as f:
        chunk = f.read(2048)
        if b'"samples":' in chunk:
            has_samples_key = True
    
    prefix = "samples.item" if has_samples_key else "item"
    
    # Count samples
    with open(input_path, 'rb') as f:
        for _ in ijson.items(f, prefix):
            num_samples += 1
    print(f"  Found {num_samples} samples")
    
    # Create memmaps
    mm_ids = np.memmap(os.path.join(output_dir, "card_ids.npy"), dtype='int32', mode='w+', shape=(num_samples, seq_len))
    mm_feats = np.memmap(os.path.join(output_dir, "card_features.npy"), dtype='float32', mode='w+', shape=(num_samples, seq_len, 11))
    mm_lbls = np.memmap(os.path.join(output_dir, "labels.npy"), dtype='int32', mode='w+', shape=(num_samples,))
    mm_outs = np.memmap(os.path.join(output_dir, "outcomes.npy"), dtype='float32', mode='w+', shape=(num_samples, 1))
    
    # Stream data
    with open(input_path, 'rb') as f:
        idx = 0
        for s in ijson.items(f, prefix):
            c_ids = s.get('card_ids', [])
            ln = min(len(c_ids), seq_len)
            if ln > 0:
                mm_ids[idx, :ln] = c_ids[:ln]
            
            c_feats = s.get('card_features', [])
            if c_feats:
                feat_arr = np.array(c_feats, dtype=np.float32)
                ln = min(feat_arr.shape[0], seq_len)
                if ln > 0:
                    mm_feats[idx, :ln] = feat_arr[:ln]
            
            mm_lbls[idx] = s.get('action_label', 0)
            mm_outs[idx] = s.get('game_outcome', 0.0)
            idx += 1
            
            if idx % 10000 == 0:
                sys.stdout.write(f"\r  Processed {idx}/{num_samples}...")
                sys.stdout.flush()
    
    # Flush and save metadata
    mm_ids.flush(); mm_feats.flush(); mm_lbls.flush(); mm_outs.flush()
    
    meta = {'num_samples': num_samples, 'seq_len': seq_len, 'feature_dim': 11}
    with open(os.path.join(output_dir, "metadata.json"), 'w') as f:
        json.dump(meta, f)
    
    print(f"\n  Conversion complete ({num_samples} samples)")
    return output_dir


def convert_mlx_to_pytorch(mlx_path, pt_path, large=False):
    """Convert MLX weights to PyTorch model (inline version)."""
    import torch
    from ai.transformer_model import CardTransformer as TorchTransformer
    
    print(f"Converting MLX model to PyTorch...")
    mlx_weights = mx.load(mlx_path)
    
    if large:
        pt_model = TorchTransformer(hidden_dim=256, num_layers=6, num_heads=8, dropout=0.2)
    else:
        pt_model = TorchTransformer(hidden_dim=128, num_layers=4, num_heads=4)
    
    pt_state = pt_model.state_dict()
    new_state = {}
    matched = 0
    
    for key, val in mlx_weights.items():
        val_np = np.array(val)
        val_pt = torch.from_numpy(val_np)
        
        if key in pt_state:
            if pt_state[key].shape != val_pt.shape:
                if len(val_pt.shape) == 2 and val_pt.shape[::-1] == pt_state[key].shape:
                    val_pt = val_pt.T
                else:
                    continue
            new_state[key] = val_pt
            matched += 1
    
    pt_model.load_state_dict(new_state, strict=False)
    os.makedirs(os.path.dirname(pt_path) or '.', exist_ok=True)
    torch.save(pt_model.state_dict(), pt_path)
    print(f"  Saved PyTorch model to {pt_path} ({matched} layers)")


def batch_iterate(batch_size, *args):
    """Yield batches of data."""
    num_samples = len(args[0])
    perm = np.random.permutation(num_samples)
    for i in range(0, num_samples, batch_size):
        ids = perm[i : i + batch_size]
        yield tuple(arg[ids] if isinstance(arg, (np.ndarray, np.generic)) else arg[mx.array(ids)] for arg in args)

class MLXImitationTrainer:
    def __init__(self, model, learning_rate=1e-4):
        self.model = model
        self.optimizer = optim.AdamW(learning_rate=learning_rate)

    def load_memmap_dataset(self, dir_path):
        """Load dataset from numpy memory maps (disk-based)."""
        print(f"  Loading memory maps from {dir_path}...")
        with open(os.path.join(dir_path, "metadata.json"), 'r') as f:
            meta = json.load(f)
        
        num_samples = meta['num_samples']
        seq_len = meta['seq_len']
        
        mm_ids = np.memmap(os.path.join(dir_path, "card_ids.npy"), dtype='int32', mode='r', shape=(num_samples, seq_len))
        mm_feats = np.memmap(os.path.join(dir_path, "card_features.npy"), dtype='float32', mode='r', shape=(num_samples, seq_len, 11))
        mm_lbls = np.memmap(os.path.join(dir_path, "labels.npy"), dtype='int32', mode='r', shape=(num_samples,))
        mm_outs = np.memmap(os.path.join(dir_path, "outcomes.npy"), dtype='float32', mode='r', shape=(num_samples, 1))
        
        return mm_ids, mm_feats, mm_lbls, mm_outs

    def load_streaming(self, filepath):
        """Iteratively load JSON to stay within RAM limits."""
        print(f"  Scanning {filepath} to count samples...")
        num_samples = 0
        has_samples_key = False
        with open(filepath, 'rb') as f:
            chunk = f.read(2048)
            if b'"samples":' in chunk:
                has_samples_key = True
        prefix = "samples.item" if has_samples_key else "item"
        with open(filepath, 'rb') as f:
            for _ in ijson.items(f, prefix):
                num_samples += 1
        
        print(f"  Found {num_samples} samples. Allocating memory...")
        seq_len = 24
        np_c_ids = np.zeros((num_samples, seq_len), dtype=np.int32)
        np_c_feats = np.zeros((num_samples, seq_len, 11), dtype=np.float32)
        np_lbls = np.zeros(num_samples, dtype=np.int32)
        np_outs = np.zeros((num_samples, 1), dtype=np.float32)
        
        print(f"  Streaming data into buffers...")
        with open(filepath, 'rb') as f:
            idx = 0
            for s in ijson.items(f, prefix):
                c_ids = s.get('card_ids')
                if c_ids:
                    ln = min(len(c_ids), seq_len)
                    np_c_ids[idx, :ln] = c_ids[:ln]
                c_feats = s.get('card_features')
                if c_feats:
                    feat_arr = np.array(c_feats, dtype=np.float32)
                    ln = min(feat_arr.shape[0], seq_len)
                    if ln > 0:
                        np_c_feats[idx, :ln] = feat_arr[:ln]
                np_lbls[idx] = s.get('action_label', 0)
                np_outs[idx] = s.get('game_outcome', 0.0)
                idx += 1
                if idx % 50000 == 0:
                    sys.stdout.write(f"\r  Loaded {idx}/{num_samples}...")
                    sys.stdout.flush()
        
        print(f"\n  Moving to Unified Memory...")
        return mx.array(np_c_ids), mx.array(np_c_feats), mx.array(np_c_ids != 0), mx.array(np_lbls), mx.array(np_outs)

    def train(self, data_path, epochs=50, batch_size=1024, save_path="models/mlx_model.npz"):

        # ... loading logic ...
        use_memmap = False
        if os.path.isdir(data_path) and os.path.exists(os.path.join(data_path, "metadata.json")):
            print("Detected Binary Memmap Dataset (Disk-Based Training)")
            t_ids, t_feats, t_lbls, t_outs = self.load_memmap_dataset(data_path)
            t_mask = None 
            use_memmap = True
        else:
            t_ids, t_feats, t_mask, t_lbls, t_outs = self.load_streaming(data_path)
        
        print("  Splitting validation set...")
        split = int(len(t_ids) * 0.9)
        v_ids, v_feats, v_lbls, v_outs = t_ids[split:], t_feats[split:], t_lbls[split:], t_outs[split:]
        t_ids, t_feats, t_lbls, t_outs = t_ids[:split], t_feats[:split], t_lbls[:split], t_outs[:split]
        
        if not use_memmap:
             v_mask = t_mask[split:]
             t_mask = t_mask[:split]

        print(f"Starting Training on {len(t_ids)} samples (MPS/GPU)")
        best_acc = 0.0
        
        # Capture model reference for use in loss function
        model = self.model
        
        # Define loss function - model accessed via closure, NOT as argument
        def loss_fn(c_ids, c_feats, mask, lbls, outs):
            logits, value = model(c_ids, c_feats, mask)
            p_loss = mx.mean(nn.losses.cross_entropy(logits, lbls))
            v_loss = mx.mean(nn.losses.mse_loss(value, outs))
            return p_loss + 0.5 * v_loss

        # Create value_and_grad wrapper - computes gradients w.r.t model's trainable params
        loss_and_grad_fn = nn.value_and_grad(model, loss_fn)

        def eval_step(c_ids, c_feats, mask, lbls):
            logits, _ = self.model(c_ids, c_feats, mask)
            preds = mx.argmax(logits, axis=1)
            correct = mx.sum(preds == lbls)
            return correct

        for epoch in range(epochs):
            self.model.train()
            start = time.time()
            total_loss = 0.0
            steps = 0
            
            dataset_inputs = (t_ids, t_feats, t_lbls, t_outs) if use_memmap else (t_ids, t_feats, t_mask, t_lbls, t_outs)
            
            if epoch == 0:
                print("  Entering training loop...")
                
            for batch_idx, batch in enumerate(batch_iterate(batch_size, *dataset_inputs)):
                if use_memmap:
                    b_ids, b_feats, b_lbls, b_outs = batch
                    b_ids, b_feats, b_lbls, b_outs = mx.array(b_ids), mx.array(b_feats), mx.array(b_lbls), mx.array(b_outs)
                    b_mask = (b_ids != 0)
                else:
                    b_ids, b_feats, b_mask, b_lbls, b_outs = batch
                
                if epoch == 0 and batch_idx == 0:
                    print(f"  Processing batch 0 (Compiling graph)...")
                    # Debug checks
                    p_debug, _ = self.model(b_ids, b_feats, b_mask)
                    pred_debug = mx.argmax(p_debug, axis=1)
                    print(f"  Labels (first 10): {b_lbls[:10].tolist()}")
                    print(f"  Preds  (first 10): {pred_debug[:10].tolist()}")

                # Compute gradients - call loss_and_grad_fn directly
                loss, grads = loss_and_grad_fn(b_ids, b_feats, b_mask, b_lbls, b_outs)
                
                # Update optimizer
                self.optimizer.update(self.model, grads)
                
                # Sync
                mx.eval(self.model.parameters(), self.optimizer.state, loss)
                
                total_loss += loss.item()
                steps += 1


            # Validation
            self.model.eval()
            val_correct = 0
            val_total = 0
            for i in range(0, len(v_ids), batch_size):
                end = min(i + batch_size, len(v_ids))
                vb_ids, vb_feats, vb_lbls = v_ids[i:end], v_feats[i:end], v_lbls[i:end]
                vb_ids, vb_feats, vb_lbls = mx.array(vb_ids), mx.array(vb_feats), mx.array(vb_lbls)
                vb_mask = (vb_ids != 0)
                
                correct = eval_step(vb_ids, vb_feats, vb_mask, vb_lbls)
                mx.eval(correct)
                val_correct += correct.item()
                val_total += (end - i)
            
            acc = val_correct / max(val_total, 1)
            epoch_time = time.time() - start
            print(f"Epoch {epoch+1:3d} | Loss: {total_loss/steps:.4f} | Acc: {acc:.2%} | Time: {epoch_time:.1f}s")
            
            if acc > best_acc:
                best_acc = acc
                os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
                self.model.save_weights(save_path)
                print(f"  [Saved Best Model]")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MLX Imitation Trainer (Apple Silicon)")
    parser.add_argument('--data', type=str, required=True, help="JSON or binary data path")
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch-size', type=int, default=1024)
    parser.add_argument('--large', action='store_true')
    parser.add_argument('--xlarge', action='store_true')
    parser.add_argument('--lr', type=float, default=5e-4)
    parser.add_argument('--output', type=str, default="models/transformer_model.pt", 
                        help="Output path (.pt for PyTorch, .npz for MLX)")
    args = parser.parse_args()
    
    # Auto-convert JSON to binary if needed
    data_path = args.data
    temp_binary_dir = None
    
    if data_path.endswith('.json'):
        # Create cache directory based on JSON filename
        cache_dir = data_path.replace('.json', '_mlx_cache')
        
        # Check if cache exists and is up-to-date
        meta_path = os.path.join(cache_dir, "metadata.json")
        json_mtime = os.path.getmtime(data_path) if os.path.exists(data_path) else 0
        cache_mtime = os.path.getmtime(meta_path) if os.path.exists(meta_path) else 0
        
        if cache_mtime < json_mtime:
            print(f"JSON file detected, converting to binary cache...")
            convert_json_to_binary(data_path, cache_dir)
        else:
            print(f"Using cached binary data from {cache_dir}")
        
        data_path = cache_dir
    
    # Select model size
    if args.xlarge:
        model = CardTransformer(hidden_dim=512, num_layers=8, num_heads=8, dropout=0.1)
        large_flag = True  # For conversion
    elif args.large:
        model = CardTransformer(hidden_dim=256, num_layers=6, num_heads=8, dropout=0.2)
        large_flag = True
    else:
        model = CardTransformer(hidden_dim=128, num_layers=4, num_heads=4)
        large_flag = False
    
    # Train
    mlx_output = args.output.replace('.pt', '.npz') if args.output.endswith('.pt') else args.output
    trainer = MLXImitationTrainer(model, learning_rate=args.lr)
    trainer.train(data_path, epochs=args.epochs, batch_size=args.batch_size, save_path=mlx_output)
    
    # Auto-convert to PyTorch if .pt output requested
    if args.output.endswith('.pt'):
        convert_mlx_to_pytorch(mlx_output, args.output, large=large_flag)
        print(f"\nTraining complete! PyTorch model saved to: {args.output}")
    else:
        print(f"\nTraining complete! MLX model saved to: {mlx_output}")