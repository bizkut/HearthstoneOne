# HearthstoneOne AI Training Guide

## Prerequisites

```bash
cd /Users/bizkut/Downloads/Games/-HearthstoneOne
pip install torch numpy websockets
```

---

## 1. Train Main AI Model (MCTS + Policy/Value Network)

The main trainer uses AlphaZero-style self-play with MCTS.

### Quick Start
```bash
python training/trainer.py
```

### Full Options
```bash
python training/trainer.py \
    --iterations 100 \
    --games-per-iter 20 \
    --mcts-sims 50 \
    --batch-size 64 \
    --learning-rate 0.001 \
    --buffer-capacity 100000 \
    --resume-checkpoint models/run_xxx/best_model.pt
```

### Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `--iterations` | 100 | Training iterations |
| `--games-per-iter` | 20 | Self-play games per iteration |
| `--mcts-sims` | 50 | MCTS simulations per move |
| `--batch-size` | 64 | Training batch size |
| `--learning-rate` | 0.001 | Optimizer learning rate |
| `--buffer-capacity` | 100000 | Replay buffer size |
| `--resume-checkpoint` | None | Resume from checkpoint |

### Output
- Models saved to: `models/run_YYYYMMDD_HHMMSS/`
- Files: `best_model.pt`, `checkpoint_iter_N.pt`

---

## 2. Train Mulligan Policy

The mulligan trainer learns which cards to keep/replace based on game outcomes.

### Quick Start
```bash
python training/mulligan_trainer.py
```

### Full Options
```bash
python training/mulligan_trainer.py \
    --iterations 20 \
    --games 100 \
    --batch-size 32 \
    --output models/mulligan_policy.pt
```

### Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `--iterations` | 10 | Training iterations |
| `--games` | 50 | Games per iteration |
| `--batch-size` | 32 | Training batch size |
| `--output` | models/mulligan_policy.pt | Output path |

### How It Works
1. Plays games with 30% exploration (random mulligan)
2. Tracks which cards were kept vs replaced
3. Associates decisions with win/loss outcomes
4. Trains policy to maximize winning keep decisions

---

## 3. Recommended Training Sequence

### Step 1: Train Main Model (CPU ~2-4 hours, GPU ~30 min)
```bash
python training/trainer.py --iterations 50 --games-per-iter 10 --mcts-sims 25
```

### Step 2: Train Mulligan Policy (~30 min)
```bash
python training/mulligan_trainer.py --iterations 20 --games 100
```

### Step 3: Run WebSocket Server
```bash
PYTHONPATH=. python runtime/websocket_server.py --model models/run_*/best_model.pt
```

---

## 4. Using Trained Models

### WebSocket Server
```bash
PYTHONPATH=. python runtime/websocket_server.py \
    --host localhost \
    --port 9876 \
    --model models/run_20260103_211151/best_model.pt
```

The server automatically loads `mulligan_policy.pt` from the same directory if present.

### HSTracker Integration
1. Build HSTracker in Xcode
2. Enable HearthstoneOne in settings
3. Start a Hearthstone game
4. AI suggestions appear as overlays!

---

## 5. Hardware Recommendations

| Device | Training Speed | Notes |
|--------|----------------|-------|
| Apple M1/M2 (MPS) | ~2x faster than CPU | Automatic detection |
| NVIDIA GPU (CUDA) | ~5x faster than CPU | Install PyTorch with CUDA |
| CPU | Baseline | Works but slow |

Check device:
```python
from ai.device import get_best_device, print_device_info
print_device_info()
```

---

## 6. Transformer Model (Phase 6)

The Transformer model uses self-attention to learn card synergies.

### Step 1: Parse HSReplay Files
```bash
python training/replay_parser.py /path/to/replays --max-files 1000 --output replay_data.json
```

### Step 2: Train with Imitation Learning
```bash
python training/imitation_trainer.py --data replay_data.json --epochs 50 --output models/transformer_model.pt

# Test with dummy data
python training/imitation_trainer.py --dummy --epochs 10
```

### Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `--data` | - | Path to preprocessed replay data |
| `--epochs` | 50 | Training epochs |
| `--batch-size` | 32 | Batch size |
| `--lr` | 1e-4 | Learning rate |
| `--output` | models/transformer_model.pt | Output path |
| `--dummy` | False | Use dummy data for testing |

### Architecture
- 4 Transformer layers, 4 attention heads
- 128 hidden dimensions
- Compatible with CUDA 6.1+ (Pascal GPUs)

