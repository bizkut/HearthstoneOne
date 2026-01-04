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
git clone https://github.com/bizkut/HearthstoneOne.git
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

### Train Models (Complete Pipeline)

Building the AI model follows a multi-phase approach. **Follow these steps in order:**

---

#### Step 0: Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Scrape meta decks (first time only, creates data/meta_deck_lists.json)
python3 scripts/scrape_top_decks.py
```

---

#### Step 1: Generate Training Data (Heuristic)
> Fast data generation using rule-based play. Good for initial training.

```bash
python3 scripts/generate_self_play.py --num-games 10000 --output data/self_play_data.json
```
*Generates ~30k samples per 1000 games. Expect ~10 min for 10k games.*

---

#### Step 2: Train the Model (Imitation Learning)
> Supervised learning on the generated data.

```bash
# Basic training (CPU/MPS)
python3 training/imitation_trainer.py \
    --data data/self_play_data.json \
    --epochs 50 \
    --batch-size 64

# CUDA GPU Training (Recommended)
python3 training/imitation_trainer.py \
    --data data/self_play_data.json \
    --epochs 200 \
    --batch-size 4096 \
    --lr 1e-3 \
    --xlarge \
    --gpu-cache
```

| Model Size | Flag | Hidden | Layers | Params | VRAM |
|------------|------|--------|--------|--------|------|
| Default | - | 128 | 4 | ~1M | 4GB |
| Large | `--large` | 256 | 6 | ~5.5M | 8GB |
| XLarge | `--xlarge` | 512 | 8 | ~12M | 16GB |

---

#### Step 3: Generate RL Data (Neural Network)
> After training, generate higher quality data using the trained model.

**Option A: Policy Network (Fast)**
```bash
python3 scripts/generate_alphazero_play.py \
    --num-games 5000 \
    --model models/transformer_model.pt \
    --output data/rl_data.json
```
*Uses the Neural Network directly to select actions. Fast but limited lookahead.*

**Option B: Full MCTS (Highest Quality)**
```bash
python3 scripts/generate_mcts_play.py \
    --sims 50 \
    --games 1000 \
    --model models/transformer_model.pt \
    --output data/mcts_data.json
```
*Uses Monte Carlo Tree Search with the model. Slower but produces stronger play.*

| Script | Method | Speed | Quality |
|--------|--------|-------|---------|
| `generate_alphazero_play.py` | Policy Network | ⚡ Fast | Good |
| `generate_mcts_play.py` | MCTS (50 sims) | 🐢 Slow | Best |

---

#### Step 4: Iterate (AlphaZero Loop)
Repeat Steps 2-3 to improve the model:
1. Train on combined data
2. Generate new RL data with the improved model
3. Repeat until performance plateaus

```bash
# Merge datasets
python3 -c "import json; d1=json.load(open('data/self_play_data.json')); d2=json.load(open('data/rl_data.json')); d1['samples'].extend(d2['samples']); json.dump(d1, open('data/combined.json','w'))"

# Train on combined data
python3 training/imitation_trainer.py --data data/combined.json --epochs 100 --xlarge
```

---

#### Which Script Should I Use?

| Phase | Script | When to Use |
|-------|--------|-------------|
| **Bootstrap** | `generate_self_play.py` | First-time training, no model yet |
| **Iteration Loop** | `generate_alphazero_play.py` | Continuous improvement (fast) |
| **Final Polish** | `generate_mcts_play.py` | Best quality before deployment (slow) |

> [!TIP]
> For practical training, use `generate_alphazero_play.py` in your iteration loop. Save `generate_mcts_play.py` for the final training run when you want maximum quality.

---

#### Apple Silicon (MLX) Training
For M1/M2/M3/M4 Macs — **10x faster** than PyTorch on Apple Silicon:

```bash
# Same interface as PyTorch trainer - conversions happen automatically
python3 training/mlx_imitation_trainer.py \
    --data data/self_play_data.json \
    --epochs 100 \
    --batch-size 1024 \
    --large
```

**What happens automatically:**
1. JSON → Binary cache (on first run, reused afterward)
2. MLX training on Unified Memory
3. Output → PyTorch `.pt` model

| Model Size | Flag | Dataset Size | Speed |
|------------|------|--------------|-------|
| Default | - | <50k samples | ~5s/epoch |
| Large | `--large` | 50k-500k | ~8s/epoch |
| XLarge | `--xlarge` | 500k+ | ~15s/epoch |

---

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
│   ├── transformer_model.py   # CardTransformer (Main Model)
│   ├── mcts.py                # Monte Carlo Tree Search
│   ├── opponent_model.py      # Opponent Modeling (Phase 8)
│   ├── deck_classifier.py     # Archetype Detection
│   ├── encoder.py             # State Encoding
│   └── game_wrapper.py        # Simulator Interface
│
├── training/                  # 🏋️ Training Scripts
│   ├── imitation_trainer.py   # Transformer Trainer
│   └── trainer.py             # Legacy AlphaZero Trainer
│
├── scripts/                   # 🛠️ Utility Scripts
│   ├── generate_self_play.py  # Heuristic Data Generator (Step 1)
│   ├── generate_mcts_play.py  # MCTS Data Generator (Step 3)
│   ├── scrape_top_decks.py    # Meta Deck Scraper
│   └── convert_to_binary.py   # Binary Format Converter (MLX)
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
