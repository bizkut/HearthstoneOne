"""
MLX Imitation Learning Trainer for HearthstoneOne AI.

Optimized for Apple Silicon (M4 Pro).
Streaming JSON data via ijson to handle 4GB+ files within 24GB RAM.
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
    perm = mx.array(np.random.permutation(num_samples))
    for i in range(0, num_samples, batch_size):
        ids = perm[i : i + batch_size]
        yield tuple(arg[ids] for arg in args)

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

    def train(self, data_path, epochs=50, batch_size=1024, save_path="models/mlx_model.npz"):
        # Load all data into Unified Memory
        t_ids, t_feats, t_mask, t_lbls, t_outs = self.load_streaming(data_path)
        
        # Split 90/10
        print("  Splitting validation set...")
        split = int(len(t_ids) * 0.9)
        v_ids, v_feats, v_mask, v_lbls, v_outs = (
            t_ids[split:], t_feats[split:], t_mask[split:], t_lbls[split:], t_outs[split:]
        )
        t_ids, t_feats, t_mask, t_lbls, t_outs = (
            t_ids[:split], t_feats[:split], t_mask[:split], t_lbls[:split], t_outs[:split]
        )

        def loss_fn(params, c_ids, c_feats, mask, lbls, outs):
            self.model.update(params)
            policy, value = self.model(c_ids, c_feats, mask)
            log_policy = mx.log(policy + 1e-8)
            p_loss = mx.mean(nn.losses.nll_loss(log_policy, lbls))
            v_loss = mx.mean(nn.losses.mse_loss(value, outs))
            return p_loss + 0.5 * v_loss

        @mx.compile
        def train_step(c_ids, c_feats, mask, lbls, outs):
            loss_and_grad_fn = nn.value_and_grad(self.model, loss_fn)
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
            
            for batch in batch_iterate(batch_size, t_ids, t_feats, t_mask, t_lbls, t_outs):
                loss = train_step(*batch)
                mx.eval(self.model.parameters(), self.optimizer.state, loss)
                total_loss += loss.item()
                steps += 1
            
            # Validation
            self.model.eval()
            val_correct = 0
            val_total = 0
            for i in range(0, len(v_ids), batch_size):
                end = min(i + batch_size, len(v_ids))
                batch = (v_ids[i:end], v_feats[i:end], v_mask[i:end], v_lbls[i:end], v_outs[i:end])
                correct, _ = self.eval_step_fn(*batch)
                mx.eval(correct)
                val_correct += correct.item()
                val_total += (end - i)
            
            acc = val_correct / val_total
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
    args = parser.parse_args()
    
    if args.large:
        model = CardTransformer(hidden_dim=256, num_layers=6, num_heads=8, dropout=0.2)
    else:
        model = CardTransformer(hidden_dim=128, num_layers=4, num_heads=4)
        
    trainer = MLXImitationTrainer(model)
    trainer.train(args.data, epochs=args.epochs, batch_size=args.batch_size, save_path=args.output)