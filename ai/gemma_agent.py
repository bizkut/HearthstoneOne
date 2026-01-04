#!/usr/bin/env python3
"""
Gemma AI Agent for Hearthstone.

Uses fine-tuned Gemma model to predict game actions.
Integrates with the existing game infrastructure.
"""

import sys
import os
import re
from typing import Optional, List, Tuple, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check for mlx-lm
try:
    from mlx_lm import load, generate
    MLX_LM_AVAILABLE = True
except ImportError:
    MLX_LM_AVAILABLE = False

from ai.actions import Action, ActionType, ACTION_SPACE_SIZE


class GemmaAgent:
    """
    Hearthstone AI agent using Gemma LLM.
    
    Converts game states to text prompts, queries the model,
    and parses responses back to game actions.
    """
    
    def __init__(
        self,
        adapter_path: str = "models/gemma_lora",
        model_name: str = "mlx-community/gemma-3-1b-it-4bit",
        temperature: float = 0.1,
        max_tokens: int = 50,
    ):
        """
        Initialize the Gemma agent.
        
        Args:
            adapter_path: Path to LoRA adapters (None for base model)
            model_name: Base model name
            temperature: Generation temperature (lower = more deterministic)
            max_tokens: Maximum tokens to generate
        """
        if not MLX_LM_AVAILABLE:
            raise ImportError("mlx-lm required. Install with: pip install mlx-lm")
        
        self.model_name = model_name
        self.adapter_path = adapter_path
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.model = None
        self.tokenizer = None
        self._loaded = False
    
    def load(self):
        """Load the model and adapters."""
        if self._loaded:
            return
        
        print(f"Loading Gemma model: {self.model_name}")
        if self.adapter_path and os.path.exists(self.adapter_path):
            print(f"With LoRA adapters: {self.adapter_path}")
            self.model, self.tokenizer = load(self.model_name, adapter_path=self.adapter_path)
        else:
            print("Without adapters (base model)")
            self.model, self.tokenizer = load(self.model_name)
        
        self._loaded = True
        print("Model loaded successfully")
    
    def format_state(
        self,
        hand: List[Any],
        my_board: List[Any],
        enemy_board: List[Any],
        my_health: int = 30,
        enemy_health: int = 30,
        my_mana: int = 0,
        max_mana: int = 0,
    ) -> str:
        """
        Format game state as a text prompt.
        
        Args:
            hand: List of cards in hand (with .name, .cost, .attack, .health)
            my_board: My minions on board
            enemy_board: Enemy minions on board
            my_health: My hero health
            enemy_health: Enemy hero health
            my_mana: Current mana
            max_mana: Maximum mana
        
        Returns:
            Formatted text prompt
        """
        def format_card(c):
            """Format a single card."""
            name = getattr(c, 'name', str(c))
            cost = getattr(c, 'cost', 0)
            attack = getattr(c, 'attack', 0)
            health = getattr(c, 'health', 0)
            
            if attack > 0 or health > 0:
                return f"{name}({cost}/{attack}/{health})"
            else:
                return f"{name}({cost})"
        
        lines = ["Game State:"]
        lines.append(f"Mana: {my_mana}/{max_mana}")
        lines.append(f"Health: {my_health} vs {enemy_health}")
        
        if my_board:
            board_str = ", ".join(format_card(c) for c in my_board)
            lines.append(f"My Board: {board_str}")
        else:
            lines.append("My Board: empty")
        
        if hand:
            hand_str = ", ".join(format_card(c) for c in hand)
            lines.append(f"My Hand: {hand_str}")
        else:
            lines.append("My Hand: empty")
        
        if enemy_board:
            enemy_str = ", ".join(format_card(c) for c in enemy_board)
            lines.append(f"Enemy Board: {enemy_str}")
        else:
            lines.append("Enemy Board: empty")
        
        lines.append("")
        lines.append("Best Action:")
        
        return "\n".join(lines)
    
    def parse_action(self, response: str, hand: List[Any], my_board: List[Any]) -> Optional[Action]:
        """
        Parse model response into a game action.
        
        Args:
            response: Model's generated text
            hand: Current hand (for matching card names)
            my_board: Current board (for matching attacker names)
        
        Returns:
            Action object or None if parsing fails
        """
        response = response.strip().upper()
        
        # End turn
        if "END TURN" in response:
            return Action.end_turn()
        
        # Hero power
        if "HERO POWER" in response:
            return Action.hero_power()
        
        # Play card: "PLAY <card_name>"
        play_match = re.search(r"PLAY\s+(.+?)(?:\s*$|\s+TARGET)", response, re.IGNORECASE)
        if play_match:
            card_name = play_match.group(1).strip()
            # Find card in hand by name match
            for i, card in enumerate(hand):
                name = getattr(card, 'name', '').upper()
                if name and (card_name in name or name in card_name):
                    return Action.play_card(i)
            # Fallback: try first playable card
            if hand:
                return Action.play_card(0)
        
        # Attack: "ATTACK with <minion>"
        attack_match = re.search(r"ATTACK\s+(?:WITH\s+)?(.+)", response, re.IGNORECASE)
        if attack_match:
            attacker_name = attack_match.group(1).strip()
            
            # Hero attack
            if "HERO" in attacker_name.upper():
                return Action.attack(-1, -1)  # Hero attacks enemy hero
            
            # Find attacker on board
            for i, minion in enumerate(my_board):
                name = getattr(minion, 'name', '').upper()
                if name and (attacker_name in name or name in attacker_name):
                    return Action.attack(i, -1)  # Attack enemy hero by default
            
            # Fallback: first minion attacks
            if my_board:
                return Action.attack(0, -1)
        
        # Default: end turn
        return Action.end_turn()
    
    def select_action(
        self,
        hand: List[Any],
        my_board: List[Any],
        enemy_board: List[Any],
        valid_actions: Optional[List[Action]] = None,
        **state_kwargs
    ) -> Action:
        """
        Select the best action for the current game state.
        
        Args:
            hand: Cards in hand
            my_board: My board minions
            enemy_board: Enemy board minions
            valid_actions: Optional list of valid actions to filter
            **state_kwargs: Additional state info (health, mana, etc.)
        
        Returns:
            Selected Action
        """
        if not self._loaded:
            self.load()
        
        # Format prompt
        prompt = "<bos>" + self.format_state(hand, my_board, enemy_board, **state_kwargs)
        
        # Generate response
        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=self.max_tokens,
            temp=self.temperature,
        )
        
        # Parse action
        action = self.parse_action(response, hand, my_board)
        
        # Validate against valid actions if provided
        if valid_actions and action not in valid_actions:
            # Find closest valid action
            for va in valid_actions:
                if va.action_type == action.action_type:
                    return va
            # Fallback to end turn or first valid action
            for va in valid_actions:
                if va.action_type == ActionType.END_TURN:
                    return va
            return valid_actions[0] if valid_actions else action
        
        return action
    
    def get_action_index(
        self,
        hand: List[Any],
        my_board: List[Any],
        enemy_board: List[Any],
        **state_kwargs
    ) -> int:
        """
        Get action as an index (for compatibility with other agents).
        
        Returns:
            Action index (0-174)
        """
        action = self.select_action(hand, my_board, enemy_board, **state_kwargs)
        return action.to_index()


def test_agent():
    """Test the Gemma agent with sample states."""
    print("Testing Gemma Agent...")
    
    # Create mock cards for testing
    class MockCard:
        def __init__(self, name, cost, attack=0, health=0):
            self.name = name
            self.cost = cost
            self.attack = attack
            self.health = health
    
    # Sample game state
    hand = [
        MockCard("Fireball", 4),
        MockCard("Frostbolt", 2),
        MockCard("Azure Drake", 5, 4, 4),
    ]
    my_board = [
        MockCard("Water Elemental", 4, 3, 6),
    ]
    enemy_board = [
        MockCard("Knife Juggler", 2, 2, 2),
    ]
    
    agent = GemmaAgent()
    
    # Test formatting
    prompt = agent.format_state(
        hand, my_board, enemy_board,
        my_health=24, enemy_health=18,
        my_mana=6, max_mana=10
    )
    print("\n--- Sample Prompt ---")
    print(prompt)
    print("---------------------\n")
    
    # Test with model (if available)
    try:
        agent.load()
        action = agent.select_action(
            hand, my_board, enemy_board,
            my_health=24, enemy_health=18,
            my_mana=6, max_mana=10
        )
        print(f"Selected action: {action}")
    except Exception as e:
        print(f"Could not load model: {e}")
        print("Testing action parsing instead...")
        
        # Test parsing
        test_responses = [
            "PLAY Fireball",
            "ATTACK with Water Elemental",
            "USE HERO POWER",
            "END TURN",
        ]
        for resp in test_responses:
            action = agent.parse_action(resp, hand, my_board)
            print(f"  '{resp}' -> {action}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gemma AI Agent')
    parser.add_argument('--test', action='store_true', help='Run test')
    parser.add_argument('--adapters', type=str, default='models/gemma_lora',
                        help='Path to LoRA adapters')
    parser.add_argument('--model', type=str, default='mlx-community/gemma-3-1b-it-4bit',
                        help='Base model')
    
    args = parser.parse_args()
    
    if args.test:
        test_agent()
    else:
        parser.print_help()
