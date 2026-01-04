"""
MLX Imitation Learning Trainer for HearthstoneOne AI.

Optimized for Apple Silicon (M4 Pro).
Streaming JSON data via ijson or binary memmaps to handle 50GB+ files within 24GB RAM.
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
    # Use numpy for permutation to support both numpy/memmap and mx.array slicing safely
    perm = np.random.permutation(num_samples)
    for i in range(0, num_samples, batch_size):
        ids = perm[i : i + batch_size]
        # Check if arg is MLX array or Numpy/Memmap to slice correctly
        # MLX arrays support numpy indices, but numpy arrays don't support MLX indices well
        yield tuple(arg[ids] if isinstance(arg, (np.ndarray, np.generic)) else arg[mx.array(ids)] for arg in args)

class MLXImitationTrainer:
    def __init__(self, model, learning_rate=1e-4):
        self.model = model
        self.optimizer = optim.AdamW(learning_rate=learning_rate)
        self.eval_step_fn = mx.compile(self._eval_step)

    def _eval_step(self, card_ids, card_features, mask, action_labels, outcomes):
        policy, value = self.model(card_ids, card_features, mask)
        predictions = mx.argmax(policy, axis=1)
        correct = mx.sum(predictions == action_labels)
        
        log_policy = mx.log(policy + 1e-8)
        policy_loss = nn.losses.nll_loss(log_policy, action_labels)
        value_loss = nn.losses.mse_loss(value, outcomes)
        
        return correct, policy_loss + 0.5 * value_loss

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
        mx_c_ids = mx.array(np_c_ids)
        mx_c_feats = mx.array(np_c_feats)
        mx_lbls = mx.array(np_lbls)
        mx_outs = mx.array(np_outs)
        mx_mask = (mx_c_ids != 0)
        
        # Free heavy numpy buffers immediately
        del np_c_ids, np_c_feats, np_lbls, np_outs
        import gc
        gc.collect()
        
        return mx_c_ids, mx_c_feats, mx_mask, mx_lbls, mx_outs

    def load_memmap_dataset(self, dir_path):
        """Load dataset from numpy memory maps (disk-based)."""
        print(f"  Loading memory maps from {dir_path}...")
        with open(os.path.join(dir_path, "metadata.json"), 'r') as f:
            meta = json.load(f)
        
        num_samples = meta['num_samples']
        seq_len = meta['seq_len']
        
        # Load memmaps in Read-Only mode (OS handles caching)
        mm_ids = np.memmap(os.path.join(dir_path, "card_ids.npy"), dtype='int32', mode='r', shape=(num_samples, seq_len))
        mm_feats = np.memmap(os.path.join(dir_path, "card_features.npy"), dtype='float32', mode='r', shape=(num_samples, seq_len, 11))
        mm_lbls = np.memmap(os.path.join(dir_path, "labels.npy"), dtype='int32', mode='r', shape=(num_samples,))
        mm_outs = np.memmap(os.path.join(dir_path, "outcomes.npy"), dtype='float32', mode='r', shape=(num_samples, 1))
        
        return mm_ids, mm_feats, mm_lbls, mm_outs

    def train(self, data_path, epochs=50, batch_size=1024, save_path="models/mlx_model.npz"):
        # Detect Input Type
        use_memmap = False
        if os.path.isdir(data_path) and os.path.exists(os.path.join(data_path, "metadata.json")):
            print("Detected Binary Memmap Dataset (Disk-Based Training)")
            t_ids, t_feats, t_lbls, t_outs = self.load_memmap_dataset(data_path)
            # Mask is not stored, we'll handle it
            t_mask = None 
            use_memmap = True
        else:
            # Load all data into Unified Memory (RAM)
            t_ids, t_feats, t_mask, t_lbls, t_outs = self.load_streaming(data_path)
        
        # Split 90/10
        print("  Splitting validation set...")
        split = int(len(t_ids) * 0.9)
        
        # Slicing memmaps returns new memmaps (views), which is fine.
        v_ids, v_feats, v_lbls, v_outs = t_ids[split:], t_feats[split:], t_lbls[split:], t_outs[split:]
        t_ids, t_feats, t_lbls, t_outs = t_ids[:split], t_feats[:split], t_lbls[:split], t_outs[:split]
        
        if not use_memmap:
             v_mask = t_mask[split:]
             t_mask = t_mask[:split]
        else:
             t_mask = None
             v_mask = None

        def loss_fn_standard(params, c_ids, c_feats, mask, lbls, outs):
             self.model.update(params)
             policy, value = self.model(c_ids, c_feats, mask)
             log_policy = mx.log(policy + 1e-8)
             p_loss = mx.mean(nn.losses.nll_loss(log_policy, lbls))
             v_loss = mx.mean(nn.losses.mse_loss(value, outs))
             return p_loss + 0.5 * v_loss

        @mx.compile
        def train_step(c_ids, c_feats, mask, lbls, outs):
            loss_and_grad_fn = nn.value_and_grad(self.model, loss_fn_standard)
            loss, grads = loss_and_grad_fn(self.model.trainable_parameters(), c_ids, c_feats, mask, lbls, outs)
            self.optimizer.update(self.model, grads)
            return loss

        print(f"Starting Training on {len(t_ids)} samples (MPS/GPU)")
        best_acc = 0.0
        
        for epoch in range(epochs):
            self.model.train()
            start = time.time()
            total_loss = 0.0
            steps = 0
            
            # Create iterator
            if use_memmap:
                dataset_inputs = (t_ids, t_feats, t_lbls, t_outs)
            else:
                dataset_inputs = (t_ids, t_feats, t_mask, t_lbls, t_outs)
                
            for batch_idx, batch in enumerate(batch_iterate(batch_size, *dataset_inputs)):
                if use_memmap:
                    # Unpack 4 args
                    b_ids, b_feats, b_lbls, b_outs = batch
                    # Create mask (numpy)
                    b_mask = (b_ids != 0)
                    # Convert to MLX
                    b_ids = mx.array(b_ids)
                    b_feats = mx.array(b_feats)
                    b_mask = mx.array(b_mask)
                    b_lbls = mx.array(b_lbls)
                    b_outs = mx.array(b_outs)
                    
                    # Debug print for first batch of first epoch
                    if epoch == 0 and batch_idx == 0:
                        print(f"DEBUG: Checking labels and predictions...")
                        # Run forward pass without update to check initial state
                        p, _ = self.model(b_ids, b_feats, b_mask)
                        pred = mx.argmax(p, axis=1)
                        print(f"  Labels (first 10): {b_lbls[:10].tolist()}")
                        print(f"  Preds  (first 10): {pred[:10].tolist()}")
                        print(f"  Label Min/Max: {mx.min(b_lbls).item()}/{mx.max(b_lbls).item()}")
                    
                    loss = train_step(b_ids, b_feats, b_mask, b_lbls, b_outs)
                else:
                    # RAM mode debug
                    if epoch == 0 and batch_idx == 0:
                        b_ids, b_feats, b_mask, b_lbls, b_outs = batch
                        print(f"DEBUG: Checking labels and predictions (RAM mode)...")
                        p, _ = self.model(b_ids, b_feats, b_mask)
                        pred = mx.argmax(p, axis=1)
                        print(f"  Labels (first 10): {b_lbls[:10].tolist()}")
                        print(f"  Preds  (first 10): {pred[:10].tolist()}")

                    loss = train_step(*batch)
                
                mx.eval(self.model.parameters(), self.optimizer.state, loss)
                total_loss += loss.item()
                steps += 1
            
            # Validation
            self.model.eval()
            val_correct = 0
            val_total = 0
            
            # Validation Loop
            for i in range(0, len(v_ids), batch_size):
                end = min(i + batch_size, len(v_ids))
                
                # Slicing
                vb_ids = v_ids[i:end]
                vb_feats = v_feats[i:end]
                vb_lbls = v_lbls[i:end]
                vb_outs = v_outs[i:end]
                
                if use_memmap:
                    vb_mask = (vb_ids != 0)
                    # Convert
                    vb_ids = mx.array(vb_ids)
                    vb_feats = mx.array(vb_feats)
                    vb_mask = mx.array(vb_mask)
                    vb_lbls = mx.array(vb_lbls)
                    vb_outs = mx.array(vb_outs)
                else:
                    vb_mask = v_mask[i:end]
                
                correct, _ = self.eval_step_fn(vb_ids, vb_feats, vb_mask, vb_lbls, vb_outs)
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
    parser.add_argument('--output', type=str, default="models/mlx_model.npz")
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    args = parser.parse_args()
    
    if args.large:
        model = CardTransformer(hidden_dim=256, num_layers=6, num_heads=8, dropout=0.2)
    else:
        model = CardTransformer(hidden_dim=128, num_layers=4, num_heads=4)
        
    trainer = MLXImitationTrainer(model, learning_rate=args.lr)
    trainer.train(args.data, epochs=args.epochs, batch_size=args.batch_size, save_path=args.output)
