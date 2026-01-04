"""
MLX Imitation Learning Trainer for HearthstoneOne AI.

Optimized for Apple Silicon (M4 Pro).
Uses pure functional state updates to ensure weights commit correctly on GPU.
"""

import os
import sys
import time
import json
import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import ijson

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.mlx_transformer_model import CardTransformer

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
        
        # Define training steps locally to capture self.model correctly
        def loss_fn(model, c_ids, c_feats, mask, lbls, outs):
            logits, value = model(c_ids, c_feats, mask)
            p_loss = mx.mean(nn.losses.cross_entropy(logits, lbls))
            v_loss = mx.mean(nn.losses.mse_loss(value, outs))
            return p_loss + 0.5 * v_loss

        # Capture self.model in the closure of the compiled function
        # We perform the value_and_grad transform on the model structure
        loss_and_grad_fn = nn.value_and_grad(self.model, loss_fn)

        @mx.compile
        def step_fn(c_ids, c_feats, mask, lbls, outs):
            # We must pass self.model to the transformed function
            loss, grads = loss_and_grad_fn(self.model, c_ids, c_feats, mask, lbls, outs)
            return loss, grads

        @mx.compile
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

                # Compute gradients
                loss, grads = step_fn(b_ids, b_feats, b_mask, b_lbls, b_outs)
                
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, required=True)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch-size', type=int, default=1024)
    parser.add_argument('--large', action='store_true')
    parser.add_argument('--lr', type=float, default=5e-4)
    parser.add_argument('--output', type=str, default="models/mlx_model.npz")
    args = parser.parse_args()
    
    if args.large:
        model = CardTransformer(hidden_dim=256, num_layers=6, num_heads=8, dropout=0.2)
    else:
        model = CardTransformer(hidden_dim=128, num_layers=4, num_heads=4)
        
    trainer = MLXImitationTrainer(model, learning_rate=args.lr)
    trainer.train(args.data, epochs=args.epochs, batch_size=args.batch_size, save_path=args.output)