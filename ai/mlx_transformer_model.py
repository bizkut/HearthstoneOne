"""
Transformer-based Model for HearthstoneOne AI (MLX Port).

Uses self-attention to learn card relationships and synergies.
Optimized for Apple Silicon.
"""

import mlx.core as mx
import mlx.nn as nn
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
        # padding_idx is not directly supported in mlx.nn.Embedding constructor in earlier versions,
        # but we can mask it manually if needed. 
        # However, for simplicity, we'll just embed everything and rely on masking in the transformer.
        self.card_id_embedding = nn.Embedding(num_cards, card_id_dim)
        
        # Feature projection
        # Input: card_id_dim + 3 (cost/atk/hp) + 4 (type) + 3 (zone) + 1 (controller) = card_id_dim + 11
        self.feature_dim = card_id_dim + 11
        self.projection = nn.Linear(self.feature_dim, hidden_dim)
        
    def __call__(self, 
                card_ids: mx.array,      # [batch, seq_len]
                card_features: mx.array  # [batch, seq_len, 11]
               ) -> mx.array:
        """
        Embed cards into hidden dimension.
        
        Returns:
            [batch, seq_len, hidden_dim]
        """
        # Get card ID embeddings
        id_emb = self.card_id_embedding(card_ids)  # [batch, seq_len, card_id_dim]
        
        # Concatenate with features
        # Note: concatenate is in mlx.core, not tensor methods
        combined = mx.concatenate([id_emb, card_features], axis=-1)  # [batch, seq_len, feature_dim]
        
        # Project to hidden dimension
        return self.projection(combined)


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding for sequence order."""
    
    def __init__(self, hidden_dim: int, max_len: int = MAX_SEQUENCE_LENGTH):
        super().__init__()
        
        # We don't register buffers in MLX models typically, just create constants
        # But since we want to save/load it with state_dict if it were learnable (it isn't),
        # we can just compute it on the fly or store it as an attribute.
        # Since it's constant, we'll compute it in __init__ and treat it as a frozen parameter or just a constant array.
        
        pe = mx.zeros((max_len, hidden_dim))
        position = mx.arange(0, max_len, dtype=mx.float32).reshape(-1, 1)
        div_term = mx.exp(mx.arange(0, hidden_dim, 2, dtype=mx.float32) * (-math.log(10000.0) / hidden_dim))
        
        # Use simple indexing for assignment
        pe[:, 0::2] = mx.sin(position * div_term)
        pe[:, 1::2] = mx.cos(position * div_term)
        
        self._pe = pe.reshape(1, max_len, hidden_dim)
        self.freeze() # Prevent updates if this was a parameter
        
    def __call__(self, x: mx.array) -> mx.array:
        """Add positional encoding to input."""
        return x + self._pe[:, :x.shape[1], :]


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
        
        # Archetype embedding
        self.archetype_embedding = nn.Embedding(num_archetypes, hidden_dim)
        
        # Positional encoding
        self.pos_encoding = PositionalEncoding(hidden_dim)
        
        # Transformer encoder layers
        self.layers = [
            nn.TransformerEncoderLayer(
                dims=hidden_dim,
                num_heads=num_heads,
                mlp_dims=hidden_dim * 4,
                dropout=dropout,
                norm_first=False # PyTorch default is False (Post-Norm), MLX Default is usually Pre-Norm check?
                # Actually PyTorch default is batch_first=True in our code, and norm_first=False.
                # MLX TransformerEncoderLayer: dims, num_heads, mlp_dims=None, dropout=0.0, activation=nn.relu, norm_first=False
            )
            for _ in range(num_layers)
        ]
        
        # [CLS] token embedding (learnable)
        self.cls_token = mx.random.normal((1, 1, hidden_dim))
        
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
        
    def __call__(self,
                card_ids: mx.array,        # [batch, seq_len]
                card_features: mx.array,   # [batch, seq_len, 11]
                mask: Optional[mx.array] = None,  # [batch, seq_len]
                archetype_id: Optional[mx.array] = None     # [batch]
               ) -> Tuple[mx.array, mx.array]:
        """
        Forward pass.
        
        Returns:
            policy: Action probabilities [batch, action_dim]
            value: State value [batch, 1]
        """
        batch_size = card_ids.shape[0]
        
        # Embed cards
        x = self.card_embedding(card_ids, card_features)  # [batch, seq_len, hidden_dim]
        
        # Add CLS token at the beginning
        # Expand cls_token to batch size
        cls_tokens = mx.broadcast_to(self.cls_token, (batch_size, 1, self.hidden_dim))
        x = mx.concatenate([cls_tokens, x], axis=1)  # [batch, seq_len+1, hidden_dim]
        
        # Add archetype embedding as additional token if provided
        if archetype_id is not None:
            archetype_embed = self.archetype_embedding(archetype_id)  # [batch, hidden_dim]
            archetype_embed = mx.expand_dims(archetype_embed, axis=1)  # [batch, 1, hidden_dim]
            x = mx.concatenate([x, archetype_embed], axis=1)  # [batch, seq_len+2, hidden_dim]
        
        # Add positional encoding
        x = self.pos_encoding(x)
        
        # Create attention mask
        # MLX MultiHeadAttention takes mask of shape (batch, num_heads, q_len, k_len) or (batch, q_len, k_len)
        # where -inf means masked, 0 means allowed.
        # PyTorch src_key_padding_mask: True for masked.
        # Here we have `mask` (from input) where True = valid, so False = masked? 
        # In `ImitationTrainer.py`: attention_mask = (card_ids != 0) -> True=Valid.
        
        attn_mask = None
        if mask is not None:
            # Add mask for CLS token (always valid)
            cls_mask = mx.ones((batch_size, 1))
            full_mask = mx.concatenate([cls_mask, mask.astype(mx.float32)], axis=1)
            
            if archetype_id is not None:
                arch_mask = mx.ones((batch_size, 1))
                full_mask = mx.concatenate([full_mask, arch_mask], axis=1)
            
            # Create additive mask: 0 for valid, -inf for invalid
            # full_mask is 1 for valid, 0 for invalid
            # We want: 1 -> 0, 0 -> -inf
            # (1 - full_mask) * -1e9
            attn_mask = (1.0 - full_mask) * -1e9
            
            # Shape for attention: (batch, seq_len, seq_len)
            # Broadcasting works, but MLX TransformerEncoderLayer expects mask to be compatible with attention
            attn_mask = mx.expand_dims(attn_mask, axis=1) # [batch, 1, seq_len]
        
        # Transformer encoding
        for layer in self.layers:
            x = layer(x, mask=attn_mask)
        
        # Use CLS token output for classification
        cls_output = x[:, 0, :]  # [batch, hidden_dim]
        
        # Policy head
        policy_logits = self.policy_head(cls_output)
        policy = nn.softmax(policy_logits, axis=-1)
        
        # Value head
        value = mx.tanh(self.value_head(cls_output))
        
        return policy, value
