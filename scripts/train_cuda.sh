#!/bin/bash
# HearthstoneOne CUDA Training Script
# Optimal settings for NVIDIA GPUs (RTX 3090, A100, etc.)

set -e

echo "=============================================="
echo "  HearthstoneOne CUDA Training Pipeline"
echo "=============================================="

# Configuration - Adjust these based on your GPU
NUM_GAMES=${NUM_GAMES:-20000}      # Number of games to generate
BATCH_SIZE=${BATCH_SIZE:-512}       # Batch size (512 for 24GB VRAM, 256 for 12GB)
EPOCHS=${EPOCHS:-200}               # Max epochs (early stopping enabled)
LR=${LR:-5e-4}                      # Learning rate
MODEL_SIZE=${MODEL_SIZE:-xlarge}    # Model size: base, large, xlarge

echo ""
echo "Configuration:"
echo "  Games:      $NUM_GAMES"
echo "  Batch Size: $BATCH_SIZE"
echo "  Epochs:     $EPOCHS"
echo "  LR:         $LR"
echo "  Model:      $MODEL_SIZE"
echo ""

# Step 1: Install dependencies
echo "[1/4] Installing dependencies..."
pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -q -r requirements.txt

# Step 2: Scrape meta decks (if not exists)
if [ ! -f "data/meta_deck_lists.json" ]; then
    echo "[2/4] Scraping meta decks..."
    python3 scripts/scrape_top_decks.py
else
    echo "[2/4] Meta decks already exist, skipping..."
fi

# Step 3: Generate training data
echo "[3/4] Generating $NUM_GAMES games..."
python3 scripts/generate_self_play.py --num-games $NUM_GAMES --output data/self_play_data.json

# Step 4: Train model
echo "[4/4] Training model..."
if [ "$MODEL_SIZE" == "xlarge" ]; then
    python3 training/imitation_trainer.py \
        --data data/self_play_data.json \
        --epochs $EPOCHS \
        --batch-size $BATCH_SIZE \
        --lr $LR \
        --xlarge \
        --output models/transformer_model.pt
elif [ "$MODEL_SIZE" == "large" ]; then
    python3 training/imitation_trainer.py \
        --data data/self_play_data.json \
        --epochs $EPOCHS \
        --batch-size $BATCH_SIZE \
        --lr $LR \
        --large \
        --output models/transformer_model.pt
else
    python3 training/imitation_trainer.py \
        --data data/self_play_data.json \
        --epochs $EPOCHS \
        --batch-size $BATCH_SIZE \
        --lr $LR \
        --output models/transformer_model.pt
fi

echo ""
echo "=============================================="
echo "  Training Complete!"
echo "  Model saved to: models/transformer_model.pt"
echo "=============================================="
