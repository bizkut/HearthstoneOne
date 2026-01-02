import math
import numpy as np
import torch
import copy
from typing import List, Dict, Tuple, Optional

class MCTSNode:
    def __init__(self, state, parent=None, action_idx=None):
        self.state = state
        self.parent = parent
        self.action_idx = action_idx
        
        self.children = {} # Map action_idx -> MCTSNode
        self.is_expanded = False
        
        self.visit_count = 0
        self.value_sum = 0.0
        self.prior_prob = 0.0 # From Policy Head
        
    @property
    def value(self):
        if self.visit_count == 0:
            return 0
        return self.value_sum / self.visit_count

class MCTS:
    """
    Monte Carlo Tree Search implementation guided by Neural Network.
    """
    
    def __init__(self, model, encoder, game_env, c_puct=1.0, num_simulations=50):
        self.model = model
        self.encoder = encoder
        self.game_env = game_env # Reference for cloning
        self.c_puct = c_puct
        self.num_simulations = num_simulations
        
    def search(self, root_state) -> List[float]:
        """
        Run MCTS simulations starting from root_state.
        Returns action probabilities (pi vector).
        """
        root = MCTSNode(root_state)
        
        # Expand root immediately
        self._expand(root)
        
        for _ in range(self.num_simulations):
            node = root
            
            # 1. Selection
            while node.is_expanded and len(node.children) > 0:
                node = self._select_child(node)
            
            # 2. Expansion & Expansion Evaluation
            if not node.is_expanded: # Only expand if not terminal (heuristic)
                # Need to verify if state is terminal?
                # For now assume expansion handles state evaluation
                value = self._expand(node)
            else:
                # Terminal or already expanded?
                # If terminal, get value
                # Simplified: re-evaluate or use stored value?
                # Let's assume _expand returns the value for backprop
                value = 0 # Placeholder for terminal check
            
            # 3. Backpropagation (Backup)
            self._backpropagate(node, value)
            
        # Return visit counts normalized
        counts = np.zeros(self.model.action_dim)
        for action_idx, child in root.children.items():
            if action_idx < len(counts):
                counts[action_idx] = child.visit_count
        
        # Normalize to probability distribution
        if counts.sum() > 0:
            return counts / counts.sum()
        else:
            # Fallback uniform
            return np.ones(self.model.action_dim) / self.model.action_dim

    def _select_child(self, node: MCTSNode) -> MCTSNode:
        """Select child using PUCT algorithm."""
        best_score = -float('inf')
        best_child = None
        
        for action_idx, child in node.children.items():
            u = self.c_puct * child.prior_prob * math.sqrt(node.visit_count) / (1 + child.visit_count)
            # Q value (exploit) + U value (explore)
            # Perspective flip: if child is opponent's turn, value is inverted?
            # AlphaZero usually predicts value for *current* player.
            # MCTS standard backprop propagates value relative to root player or alternating?
            # Simplified: Alternating game. If state.current_player != parent.current_player, value is flipped.
            
            # Assume value is always from perspective of player who made the move to reach this state?
            # Or simpler: AlphaZero value head is P(Current Player Wins).
            # If Child State is Opponent's turn, Value Head predicts Opponent Win Prob.
            # So Q for Current Player = - Value(Child State).
            
            q_value = -child.value 
            
            score = q_value + u
            if score > best_score:
                best_score = score
                best_child = child
                
        if best_child is None:
            # Should not happen unless no children
            return node # Stuck?
            
        return best_child

    def _expand(self, node: MCTSNode) -> float:
        """
        Expand leaf node using NN prediction.
        Returns: Value of the state (Leaf evaluation).
        """
        # Encode state
        if node.state is None:
            # Should recreate state based on parent + action?
            # Or traverse?
            # For simplicity, we assume node.state is populated on creation
            # OR we populate it here if it's None (lazy eval).
            if node.parent:
                node.state = self._apply_action(node.parent.state, node.action_idx)
        
        # Simpler approach: node.game_copy object.
        game_copy = node.state # Let's assume MCTSNode holds the Wrapper/Game as 'state'
        
        # Get valid actions indices
        # We need to bridge 'Action' objects to 'Indices'
        from .game_wrapper import HearthstoneGame
        wrapper = HearthstoneGame()
        wrapper._game = game_copy # Inject the clone

        # Now we have a valid GameState from the wrapper
        tensor = self.encoder.encode(wrapper.get_state()).unsqueeze(0) # Batch dim
        
        # Predict
        self.model.eval()
        with torch.no_grad():
            policy_probs, value = self.model(tensor)
            
        value = value.item()
        
        # Mask invalid actions
        # Get valid actions for this state
        # We need a wrapper instance attached to this state/game clone?
        # The GameState object is static data. We need to query the Simulator.
        # Ideally node.state holds the Simulator Clone?
        # Let's fix MCTSNode to hold the wrapper/simulator if feasible.
        # REFACTOR: node.state should probably be the Wrapper (HearthstoneGame) instance itself
        # to allow querying actions easily. Or we maintain GameState + clone separately.
        
        
        # Simpler approach: node.game_copy object.
        # game_copy = node.state # Already done above
        
        # Get valid actions indices
        # We need to bridge 'Action' objects to 'Indices'
        # wrapper = HearthstoneGame() # Already done above
        # wrapper._game = game_copy # Inject the clone
        
        valid_actions_objs = wrapper.get_valid_actions()
        valid_indices = [a.to_index() for a in valid_actions_objs]
        if not valid_indices: 
            valid_indices = [0] # End turn fallback
            
        node.is_expanded = True
        
        # Create children
        for idx in valid_indices:
             if idx not in node.children:
                 # Lazy state creation: Pass None, create on traversal
                 # But we need to keep the PARENT alive to clone from
                 child = MCTSNode(state=None, parent=node, action_idx=idx)
                 child.prior_prob = policy_probs[0][idx].item()
                 node.children[idx] = child
        
        return value

    def _apply_action(self, parent_game, action_idx):
        """
        Apply action_idx to parent_game (Game object) and return new Game object.
        """
        # Clone parent game first
        new_game = parent_game.clone()
        
        # To execute the action, we need to decode the index
        # We need access to Action class
        from .actions import Action
        action_obj = Action.from_index(action_idx)
        
        # Execute on new_game using wrapper logic
        # We can reuse HearthstoneGame helper methods if we had them exposed statically
        # Or instantiate a temporary wrapper
        wrapper = HearthstoneGame()
        wrapper._game = new_game
        
        # Perform action
        player = wrapper.current_player
        
        # Execute based on type
        # NOTE: logic duplicated from game.py or self_play.py?
        # Ideally wrapper has `step(action)`
        
        try:
            if action_obj.action_type.name == "END_TURN":
                new_game.end_turn()
            elif action_obj.action_type.name == "PLAY_CARD":
                # Need to map index to hand card
                # Card indices might shift if hand changes? 
                # MCTS assumes static snapshot so indices are valid for THIS state.
                if action_obj.card_index < len(player.hand):
                    card = player.hand[action_obj.card_index]
                    target = None
                    # Resolve target index
                    if action_obj.target_index is not None:
                         # 0-7: Minions (offset logic from Action.to_index)
                         pass # TODO: target resolution
                    new_game.play_card(card, target) # Simplified
            elif action_obj.action_type.name == "ATTACK":
                pass # TODO: attack resolution
            elif action_obj.action_type.name == "HERO_POWER":
                new_game.use_hero_power()
                
        except Exception:
            pass # Invalid move in simulation?
            
        return new_game

    def _backpropagate(self, node: MCTSNode, value: float):
        """Update node stats up to root."""
        current = node
        while current is not None:
            current.visit_count += 1
            current.value_sum += value
            current = current.parent
            value = -value # Switch perspective for opponent
