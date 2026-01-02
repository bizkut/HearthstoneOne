import torch
import torch.nn as nn
import torch.nn.functional as F

class HearthstoneModel(nn.Module):
    """
    Neural Network for Hearthstone AI.
    
    Architecture:
    - Input: Game State Tensor
    - Hidden Layers: Fully Connected (MLP)
    - Heads:
        - Policy Head: Probabilities for each action (Action Space Size)
        - Value Head: Scalar evaluation of current state (-1 to 1)
    """
    
    def __init__(self, input_dim, action_dim):
        super(HearthstoneModel, self).__init__()
        
        self.input_dim = input_dim
        self.action_dim = action_dim
        self.hidden_dim = 256
        
        # Shared Layers
        self.fc1 = nn.Linear(input_dim, self.hidden_dim)
        self.fc2 = nn.Linear(self.hidden_dim, self.hidden_dim)
        self.dropout = nn.Dropout(0.1)
        
        # Policy Head (Actor)
        self.policy_head = nn.Linear(self.hidden_dim, action_dim)
        
        # Value Head (Critic)
        self.value_head = nn.Linear(self.hidden_dim, 1)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        
        # Policy: Logits -> Softmax
        policy_logits = self.policy_head(x)
        policy = F.softmax(policy_logits, dim=-1)
        
        # Value: Tanh (-1 to 1)
        value = torch.tanh(self.value_head(x))
        
        return policy, value
