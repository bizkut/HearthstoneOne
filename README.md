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

### Train Models
```bash
# MLP (AlphaZero self-play)
python training/trainer.py --epochs 100 --output models/

# Transformer (behavior cloning)
python training/imitation_trainer.py --data data/replays.json --epochs 50 --output models/transformer_model.pt

# Test with dummy data
python training/imitation_trainer.py --dummy --epochs 10
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
│   ├── trainer.py             # AlphaZero self-play
│   ├── imitation_trainer.py   # Behavior cloning
│   ├── replay_parser.py       # HSReplay XML parser
│   └── mulligan_trainer.py    # Mulligan policy training
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

## 🖥️ Hardware Compatibility

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
