"""
Transformer-based Model for HearthstoneOne AI.

Uses self-attention to learn card relationships and synergies.
Compatible with CUDA Compute Capability 6.1+ (Pascal GPUs).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple


# Maximum sequence lengths
MAX_HAND_SIZE = 10
MAX_BOARD_SIZE = 7
MAX_SEQUENCE_LENGTH = 1 + MAX_BOARD_SIZE + MAX_HAND_SIZE + MAX_BOARD_SIZE + 1  # [CLS] + board + hand + opp_board + [SEP]


class CardEmbedding(nn.Module):
    """
    Embeds card features into a dense vector representation.
    
    Input features per card:
    - Card ID (learned embedding)
    - Mana cost, attack, health (normalized scalars)
    - Card type (one-hot: minion, spell, weapon, hero)
    - Zone (one-hot: hand, board, graveyard)
    - Controller (friendly/enemy)
    """
    
    def __init__(self, 
                 num_cards: int = 10000,  # Vocabulary size for card IDs
                 card_id_dim: int = 64,
                 hidden_dim: int = 128):
        super().__init__()
        
        self.hidden_dim = hidden_dim
        
        # Card ID embedding (learned)
        self.card_id_embedding = nn.Embedding(num_cards, card_id_dim, padding_idx=0)
        
        # Feature projection
        # Input: card_id_dim + 3 (cost/atk/hp) + 4 (type) + 3 (zone) + 1 (controller) = card_id_dim + 11
        self.feature_dim = card_id_dim + 11
        self.projection = nn.Linear(self.feature_dim, hidden_dim)
        
    def forward(self, 
                card_ids: torch.Tensor,      # [batch, seq_len]
                card_features: torch.Tensor  # [batch, seq_len, 11]
               ) -> torch.Tensor:
        """
        Embed cards into hidden dimension.
        
        Returns:
            [batch, seq_len, hidden_dim]
        """
        # Get card ID embeddings
        id_emb = self.card_id_embedding(card_ids)  # [batch, seq_len, card_id_dim]
        
        # Concatenate with features
        combined = torch.cat([id_emb, card_features], dim=-1)  # [batch, seq_len, feature_dim]
        
        # Project to hidden dimension
        return self.projection(combined)


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding for sequence order."""
    
    def __init__(self, hidden_dim: int, max_len: int = MAX_SEQUENCE_LENGTH):
        super().__init__()
        
        pe = torch.zeros(max_len, hidden_dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, hidden_dim, 2).float() * (-math.log(10000.0) / hidden_dim))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        self.register_buffer('pe', pe.unsqueeze(0))  # [1, max_len, hidden_dim]
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input."""
        return x + self.pe[:, :x.size(1), :]


class CardTransformer(nn.Module):
    """
    Transformer encoder for Hearthstone game states.
    
    Architecture:
    - CardEmbedding for input representation
    - Positional encoding for sequence order
    - Multi-head self-attention layers
    - Policy and Value heads
    """
    
    def __init__(self,
                 num_cards: int = 10000,
                 hidden_dim: int = 128,
                 num_heads: int = 4,
                 num_layers: int = 4,
                 action_dim: int = 200,
                 dropout: float = 0.1,
                 num_archetypes: int = 6):
        super().__init__()
        
        self.hidden_dim = hidden_dim
        self.action_dim = action_dim
        self.num_archetypes = num_archetypes
        
        # Card embedding
        self.card_embedding = CardEmbedding(
            num_cards=num_cards,
            card_id_dim=64,
            hidden_dim=hidden_dim
        )
        
        # Archetype embedding (Phase 7: Meta-Aware)
        self.archetype_embedding = nn.Embedding(num_archetypes, hidden_dim)
        
        # Positional encoding
        self.pos_encoding = PositionalEncoding(hidden_dim)
        
        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 4,
            dropout=dropout,
            batch_first=True  # [batch, seq, dim]
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # [CLS] token embedding (learnable)
        self.cls_token = nn.Parameter(torch.randn(1, 1, hidden_dim))
        
        # Output heads
        self.policy_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, action_dim)
        )
        
        self.value_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1)
        )
        
    def forward(self,
                card_ids: torch.Tensor,        # [batch, seq_len]
                card_features: torch.Tensor,   # [batch, seq_len, 11]
                attention_mask: Optional[torch.Tensor] = None,  # [batch, seq_len]
                archetype_id: Optional[torch.Tensor] = None     # [batch] - Phase 7 Meta-Aware
               ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.
        
        Args:
            card_ids: Card ID indices [batch, seq_len]
            card_features: Card features [batch, seq_len, 11]
            attention_mask: Mask for padding [batch, seq_len], True = valid
            archetype_id: Optional opponent archetype index [batch] (0-5)
            
        Returns:
            policy: Action probabilities [batch, action_dim]
            value: State value [batch, 1]
        """
        batch_size = card_ids.size(0)
        
        # Embed cards
        x = self.card_embedding(card_ids, card_features)  # [batch, seq_len, hidden_dim]
        
        # Add CLS token at the beginning
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)  # [batch, 1, hidden_dim]
        x = torch.cat([cls_tokens, x], dim=1)  # [batch, seq_len+1, hidden_dim]
        
        # Add archetype embedding as additional token if provided (Phase 7)
        if archetype_id is not None:
            archetype_embed = self.archetype_embedding(archetype_id)  # [batch, hidden_dim]
            archetype_embed = archetype_embed.unsqueeze(1)  # [batch, 1, hidden_dim]
            x = torch.cat([x, archetype_embed], dim=1)  # [batch, seq_len+2, hidden_dim]
        
        # Add positional encoding
        x = self.pos_encoding(x)
        
        # Create attention mask for transformer (True = masked out)
        if attention_mask is not None:
            # Add mask for CLS token (always valid)
            cls_mask = torch.ones(batch_size, 1, device=attention_mask.device, dtype=torch.bool)
            attention_mask = torch.cat([cls_mask, attention_mask], dim=1)
            # Add mask for archetype token if present
            if archetype_id is not None:
                arch_mask = torch.ones(batch_size, 1, device=attention_mask.device, dtype=torch.bool)
                attention_mask = torch.cat([attention_mask, arch_mask], dim=1)
            # Invert: transformer expects True = ignored
            src_key_padding_mask = ~attention_mask
        else:
            src_key_padding_mask = None
        
        # Transformer encoding
        x = self.transformer(x, src_key_padding_mask=src_key_padding_mask)
        
        # Use CLS token output for classification
        cls_output = x[:, 0, :]  # [batch, hidden_dim]
        
        # Policy head
        policy_logits = self.policy_head(cls_output)
        policy = F.softmax(policy_logits, dim=-1)
        
        # Value head
        value = torch.tanh(self.value_head(cls_output))
        
        return policy, value


class SequenceEncoder:
    """
    Encodes a game state into sequences for the CardTransformer.
    
    Converts GameState to:
    - card_ids: [seq_len] tensor of card ID indices
    - card_features: [seq_len, 11] tensor of card features
    - attention_mask: [seq_len] tensor of valid positions
    """
    
    def __init__(self, card_to_id: dict = None):
        # Card ID vocabulary (can be loaded from CardDatabase)
        self.card_to_id = card_to_id or {}
        self.unknown_id = 1  # Reserve 0 for padding
        
    def encode(self, game_state) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Encode a GameState into transformer inputs.
        
        Returns:
            card_ids: [seq_len] tensor
            card_features: [seq_len, 11] tensor
            attention_mask: [seq_len] tensor
        """
        card_ids = []
        card_features = []
        
        # Friendly board
        for minion in game_state.friendly_player.board[:MAX_BOARD_SIZE]:
            cid, feat = self._encode_card(minion, zone=1, controller=1)
            card_ids.append(cid)
            card_features.append(feat)
        
        # Pad friendly board
        for _ in range(MAX_BOARD_SIZE - len(game_state.friendly_player.board)):
            card_ids.append(0)
            card_features.append([0] * 11)
        
        # Friendly hand
        for card in game_state.friendly_player.hand[:MAX_HAND_SIZE]:
            cid, feat = self._encode_card(card, zone=0, controller=1)
            card_ids.append(cid)
            card_features.append(feat)
        
        # Pad hand
        for _ in range(MAX_HAND_SIZE - len(game_state.friendly_player.hand)):
            card_ids.append(0)
            card_features.append([0] * 11)
        
        # Enemy board
        for minion in game_state.enemy_player.board[:MAX_BOARD_SIZE]:
            cid, feat = self._encode_card(minion, zone=1, controller=0)
            card_ids.append(cid)
            card_features.append(feat)
        
        # Pad enemy board
        for _ in range(MAX_BOARD_SIZE - len(game_state.enemy_player.board)):
            card_ids.append(0)
            card_features.append([0] * 11)
        
        # Create tensors
        card_ids_tensor = torch.tensor(card_ids, dtype=torch.long)
        card_features_tensor = torch.tensor(card_features, dtype=torch.float32)
        attention_mask = (card_ids_tensor != 0)
        
        return card_ids_tensor, card_features_tensor, attention_mask
    
    def _encode_card(self, card, zone: int, controller: int) -> Tuple[int, list]:
        """Encode a single card."""
        # Get card ID
        card_id_str = getattr(card, 'card_id', '') or getattr(card, 'id', '')
        card_id = self.card_to_id.get(card_id_str, self.unknown_id)
        
        # Get stats (normalized)
        cost = min(getattr(card, 'cost', 0), 10) / 10.0
        attack = min(getattr(card, 'attack', 0), 12) / 12.0
        health = min(getattr(card, 'health', 0), 12) / 12.0
        
        # Card type one-hot [minion, spell, weapon, hero]
        card_type = getattr(card, 'card_type', 0)
        type_onehot = [0, 0, 0, 0]
        if isinstance(card_type, int) and 0 <= card_type < 4:
            type_onehot[card_type] = 1
        
        # Zone one-hot [hand, board, graveyard]
        zone_onehot = [0, 0, 0]
        if 0 <= zone < 3:
            zone_onehot[zone] = 1
        
        features = [cost, attack, health] + type_onehot + zone_onehot + [controller]
        
        return card_id, features
