# 🃏 HearthstoneOne

> **AI Assistant for Hearthstone** — Real-time coaching + AlphaZero training + HSTracker integration

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-12.2-76B900?style=for-the-badge&logo=nvidia&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **AlphaZero AI** | Self-play training with MCTS + Deep Learning |
| 🤖 **Transformer Model** | Attention-based architecture for card synergies |
| 👁️ **Real-Time Overlay** | Arrow indicators for suggested plays |
| 🔌 **HSTracker Integration** | WebSocket bridge for seamless connectivity |
| 🎯 **Mulligan Assistant** | Learned policy for keep/replace decisions |
| 📊 **HSReplay Training** | Learn from human games via behavior cloning |

---

## 🐳 Quick Start (Docker)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (for GPU)

### 1. Start the WebSocket Server
```bash
# Start inference server with GPU
docker compose up -d

# Check logs
docker compose logs -f server
```

The server runs on `ws://localhost:9876` and connects to HSTracker.

### 2. Train the AI

**Option A: Self-Play (MLP Model)**
```bash
docker compose run train
```

**Option B: Imitation Learning (Transformer)**
```bash
# Step 1: Parse HSReplay files
mkdir -p data/replays
# Copy your .xml replay files to data/replays/

docker compose run parser

# Step 2: Train on parsed data
docker compose run imitation
```

### 3. Stop Everything
```bash
docker compose down
```

---

## 💻 Local Development

### Installation
```bash
# Clone
git clone https://github.com/Kevzi/-HearthstoneOne.git
cd HearthstoneOne

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Run WebSocket Server
```bash
python runtime/websocket_server.py --host localhost --port 9876 --model models/best_model.pt
```

### Train Models (Transformer Pipeline)

#### Quick Start
```bash
# 1. Scrape meta decks (first time only)
python3 scripts/scrape_top_decks.py

# 2. Generate training data (~2 min for 1000 games)
python3 scripts/generate_self_play.py --num-games 1000 --output data/self_play_data.json

# 3. Train the model (~6 min for 50 epochs on MPS)
python3 training/imitation_trainer.py --data data/self_play_data.json --epochs 50 --batch-size 64
```

#### Action Space
The model learns to predict which action to take:
| Label | Action |
|-------|--------|
| 0-9 | Play card from hand (index 0-9) |
| 10 | Use Hero Power |
| 11-17 | Attack with minion (board index 0-6) |
| 18 | Attack with hero (weapon) |

#### Expected Results
| Dataset Size | Epochs | Accuracy |
|--------------|--------|----------|
| 1,000 games | 50 | ~75% |
| 5,000 games | 100 | ~80%+ |
| 10,000 games | 100 | ~85%+ |

#### Advanced Training
```bash
# Generate larger dataset for better accuracy
python3 scripts/generate_self_play.py --num-games 10000 --output data/self_play_data.json

# Train with more epochs
python3 training/imitation_trainer.py --data data/self_play_data.json --epochs 100 --batch-size 128 --lr 5e-5
```

### 🚀 CUDA Server Training (Recommended)

For best results, train on a CUDA GPU server:

```bash
# One-liner for CUDA training
./scripts/train_cuda.sh

# Or with custom settings
NUM_GAMES=20000 BATCH_SIZE=512 MODEL_SIZE=xlarge ./scripts/train_cuda.sh
```

#### Model Sizes
| Flag | Hidden | Layers | Params | VRAM | Best For |
|------|--------|--------|--------|------|----------|
| (default) | 128 | 4 | ~1M | 4GB | Testing |
| `--large` | 256 | 6 | ~5.5M | 8GB | Good quality |
| `--xlarge` | 512 | 8 | ~12M | 16GB+ | Best quality |

#### CUDA Training Command
```bash
# Generate 20k games (~10 min)
python3 scripts/generate_self_play.py --num-games 20000 --output data/self_play_data.json

# Train XL model (~2 hours on RTX 3090)
python3 training/imitation_trainer.py \
    --data data/self_play_data.json \
    --epochs 200 \
    --batch-size 512 \
    --lr 5e-4 \
    --xlarge
```

### Legacy MLP Training
```bash
python training/trainer.py --epochs 100 --output models/
```

---

## 🔗 HSTracker Integration

HearthstoneOne integrates with [HSTracker](https://github.com/HearthSim/HSTracker) via WebSocket:

1. **Start the Python server** (Docker or local)
2. **HSTracker connects automatically** and streams Power.log
3. **AI suggestions appear** in the overlay with arrow indicators

### Message Protocol
```javascript
// Client → Server
{ "type": "log", "line": "..." }
{ "type": "request_suggestion" }
{ "type": "request_mulligan", "hand_cards": [...], "opponent_class": 2 }

// Server → Client
{ "type": "suggestion", "action": "play_card", "card_id": "...", "win_probability": 0.65 }
{ "type": "mulligan", "keep_probabilities": [0.9, 0.2, 0.8] }
```

---

## 📁 Project Structure

```
HearthstoneOne/
├── ai/                        # 🧠 AI Models
│   ├── model.py               # MLP policy/value network
│   ├── transformer_model.py   # Transformer with self-attention
│   ├── mcts.py                # Monte Carlo Tree Search
│   ├── encoder.py             # State encoding (690 dims)
│   ├── mulligan_policy.py     # Mulligan decision network
│   └── game_wrapper.py        # Simulator interface
│
├── training/                  # 🏋️ Training Scripts
│   ├── imitation_trainer.py   # Transformer Trainer
│   └── trainer.py             # Legacy AlphaZero Trainer
│
├── scripts/                   # 🛠️ Utility Scripts
│   ├── generate_self_play.py  # Data Generator
│   ├── scrape_top_decks.py    # Deck Scraper
│   └── fetch_meta_decks.py    # Archetype Fetcher
│
├── runtime/                   # 🔌 Runtime Services
│   ├── websocket_server.py    # WebSocket API
│   ├── parser.py              # Power.log parser
│   └── log_watcher.py         # File watcher
│
├── simulator/                 # 🎮 Game Engine
│   ├── game.py                # Game state
│   ├── player.py              # Player logic
│   └── entities.py            # Cards, Minions, Heroes
│
├── HSTracker/                 # 📱 Swift Client (macOS)
│   └── HearthstoneOne/        # WebSocket client + overlay
│
├── Dockerfile                 # 🐳 CUDA 12.2 container
├── docker-compose.yml         # Multi-service orchestration
└── requirements.txt           # Python dependencies
```

---

## 🧠 Model Architectures

### MLP (HearthstoneModel)
- Input: 690-dimensional game state vector
- Hidden: 512 → 256 neurons
- Output: Policy (action probs) + Value (-1 to +1)

### Transformer (CardTransformer)
- Input: Sequence of card embeddings
- 4 attention layers, 4 heads, 128 hidden dim
- Self-attention learns card relationships
- ~1M parameters, fast inference on Pascal GPUs

---

## 🧠 Training (Apple Silicon Optimized)

This project features a highly optimized training pipeline designed for Apple Silicon (M1/M2/M3/M4) chips, utilizing the **MLX** framework and **Unified Memory**.

### Phase 1: Imitation Learning (Warm Start)
Train the model on massive datasets (e.g., 2.7M+ samples) without RAM bottlenecks using disk-based streaming.

1.  **Prepare Data (Convert to Binary Memmap):**
    ```bash
    python3 scripts/convert_to_binary.py --input data/self_play_data2.json --output data/binary_data_large
    ```
2.  **Train with MLX (M4 Pro Optimized):**
    ```bash
    python3 training/mlx_imitation_trainer.py --data data/binary_data_large --epochs 100 --batch-size 1024 --large --lr 5e-4
    ```
    *Performance: ~2s per epoch on M4 Pro (25k subset), handles 50GB+ datasets on 24GB RAM.*

### Phase 2: AlphaZero Self-Play (RL)
Improve the model by having it play against itself and learn from the outcomes.

1.  **Convert MLX Model to PyTorch (for Inference):**
    ```bash
    python3 scripts/convert_mlx_to_pt.py --mlx models/mlx_model.npz --pt models/transformer_model.pt --large
    ```
2.  **Generate Self-Play Games:**
    ```bash
    python3 scripts/generate_alphazero_play.py --num-games 5000 --output data/rl_gen_1.json --model models/transformer_model.pt
    ```
3.  **Loop:** Convert new data -> Train (Phase 1) -> Generate -> Repeat.

### ☁️ Hugging Face Integration
Share your massive datasets with the community in optimized Parquet format.
```bash
python3 scripts/push_to_huggingface.py --input data/self_play_data2.json --repo your-username/hearthstone-replays
```

## 🛠 Installation

| GPU | Training | Inference |
|-----|----------|-----------|
| **Pascal (GTX 1080)** | ✅ | ✅ Fast |
| **Turing (RTX 2080)** | ✅ | ✅ Fast |
| **Ampere (RTX 3090)** | ✅ | ✅ Very Fast |
| **Apple Silicon (MPS)** | ✅ (with fallback) | ✅ |
| **CPU** | ✅ Slow | ✅ |

---

## 📜 License

MIT License — See [LICENSE](LICENSE)

---

<p align="center">
  <b>HearthstoneOne</b> — Open-source AI for research and education.
</p>
