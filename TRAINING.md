# 🏋️ HearthstoneOne Training Guide

Complete guide for training the HearthstoneOne AI models.

---

## 🐳 Docker Training (Recommended)

### Prerequisites
```bash
# Verify NVIDIA Container Toolkit
docker run --rm --gpus all nvidia/cuda:12.2.2-base-ubuntu22.04 nvidia-smi
```

### Training Commands

| Command | Model | Description |
|---------|-------|-------------|
| `docker compose run train` | MLP | AlphaZero self-play |
| `docker compose run imitation` | Transformer | Behavior cloning |
| `docker compose run parser` | — | Parse HSReplay XML |

---

## 1. Self-Play Training (MLP)

Trains the MLP model via AlphaZero-style self-play.

```bash
# Docker
docker compose run train

# Local
python training/trainer.py --epochs 100 --output models/
```

### Parameters
| Param | Default | Description |
|-------|---------|-------------|
| `--epochs` | 100 | Training iterations |
| `--simulations` | 50 | MCTS simulations per move |
| `--games` | 10 | Self-play games per epoch |
| `--output` | models/ | Output directory |

---

## 2. Imitation Learning (Transformer)

Trains the Transformer model on human replays.

### Step 1: Get HSReplay Files

```bash
mkdir -p data/replays

# Option A: Export from HSReplay.net
# Option B: Copy from HSTracker
cp ~/Library/Application\ Support/HSTracker/HSReplay/*.xml data/replays/
```

### Step 2: Parse Replays

```bash
# Docker
docker compose run parser

# Local
python training/replay_parser.py data/replays --output data/replays.json --max-files 1000
```

### Step 3: Train

```bash
# Docker
docker compose run imitation

# Local
python training/imitation_trainer.py --data data/replays.json --epochs 50 --output models/transformer_model.pt

# Test pipeline with dummy data
python training/imitation_trainer.py --dummy --epochs 10
```

### Parameters
| Param | Default | Description |
|-------|---------|-------------|
| `--data` | — | Path to parsed replay JSON |
| `--epochs` | 50 | Training epochs |
| `--batch-size` | 32 | Batch size |
| `--lr` | 1e-4 | Learning rate |
| `--output` | models/transformer_model.pt | Output path |

---

## 3. Mulligan Training

Trains the mulligan decision policy.

```bash
python training/mulligan_trainer.py --data data/mulligan_data.json --epochs 30 --output models/mulligan_policy.pt
```

---

## 4. WebSocket Server

Runs inference server for HSTracker.

```bash
# Docker (auto-starts with docker compose up)
docker compose up -d

# Local
python runtime/websocket_server.py --host 0.0.0.0 --port 9876 --model models/best_model.pt
```

The server auto-detects model type (MLP or Transformer).

---

## 5. Hardware

### GPU Compatibility
| GPU | CUDA | Status |
|-----|------|--------|
| Pascal (GTX 1080) | 6.1 | ✅ Works |
| Turing (RTX 2080) | 7.5 | ✅ Works |
| Ampere (RTX 3090) | 8.6 | ✅ Works |
| Apple Silicon | MPS | ✅ Works (with fallback) |

### Check Device
```python
from ai.device import print_device_info
print_device_info()
```

---

## 6. Model Architectures

### MLP (HearthstoneModel)
- 690 input features → 512 → 256 → Policy + Value
- ~500K parameters

### Transformer (CardTransformer)
- 4 layers, 4 heads, 128 hidden dim
- Self-attention for card synergies
- ~1M parameters

---

## 📁 Output Files

| File | Description |
|------|-------------|
| `models/best_model.pt` | Best MLP checkpoint |
| `models/transformer_model.pt` | Transformer checkpoint |
| `models/mulligan_policy.pt` | Mulligan policy |
| `data/replays.json` | Parsed replay data |
