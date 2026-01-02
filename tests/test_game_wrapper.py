"""Tests for the Fireplace game wrapper."""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestHearthstoneGameInit:
    """Tests for HearthstoneGame initialization."""
    
    def test_game_not_initialized_before_reset(self):
        """Game should raise error if accessed before reset."""
        from ai.game_wrapper import HearthstoneGame
        
        game = HearthstoneGame()
        with pytest.raises(RuntimeError, match="Game not initialized"):
            _ = game.game
    
    def test_perspective_default(self):
        """Default perspective should be player 1."""
        from ai.game_wrapper import HearthstoneGame
        
        game = HearthstoneGame()
        assert game.perspective == 1
    
    def test_perspective_player2(self):
        """Can set perspective to player 2."""
        from ai.game_wrapper import HearthstoneGame
        
        game = HearthstoneGame(perspective=2)
        assert game.perspective == 2


class TestHearthstoneGameReset:
    """Tests for game reset functionality."""
    
    @pytest.fixture
    def game(self):
        """Create a fresh game instance."""
        from ai.game_wrapper import HearthstoneGame
        return HearthstoneGame()
    
    def test_reset_returns_game_state(self, game):
        """Reset should return a valid GameState."""
        from ai.game_state import GameState
        
        state = game.reset()
        assert isinstance(state, GameState)
    
    def test_reset_initializes_game(self, game):
        """Reset should initialize the internal game."""
        game.reset()
        # Should not raise
        _ = game.game
    
    def test_reset_turn_is_one(self, game):
        """Game should start at turn 1."""
        state = game.reset()
        assert state.turn >= 1
    
    def test_reset_no_game_over(self, game):
        """Game should not be over immediately after reset."""
        state = game.reset()
        assert not state.is_game_over
        assert not game.is_game_over
    
    def test_reset_players_have_health(self, game):
        """Both players should have 30 health."""
        state = game.reset()
        assert state.friendly_player.hero.health == 30
        assert state.enemy_player.hero.health == 30
    
    def test_reset_players_have_cards(self, game):
        """Players should have cards in hand after mulligan."""
        state = game.reset()
        # First player gets 3 cards, second gets 4 + coin
        assert 3 <= len(state.friendly_player.hand) <= 5


class TestGetValidActions:
    """Tests for action enumeration."""
    
    @pytest.fixture
    def game(self):
        """Create a game and reset it."""
        from ai.game_wrapper import HearthstoneGame
        g = HearthstoneGame()
        g.reset()
        return g
    
    def test_returns_list(self, game):
        """Should return a list of actions."""
        actions = game.get_valid_actions()
        assert isinstance(actions, list)
    
    def test_always_has_end_turn_on_own_turn(self, game):
        """END_TURN should always be available on own turn."""
        from ai.actions import ActionType
        
        # Make sure it's our turn
        if not game.is_my_turn:
            game.game.end_turn()
        
        actions = game.get_valid_actions()
        end_turn_actions = [a for a in actions if a.action_type == ActionType.END_TURN]
        assert len(end_turn_actions) == 1
    
    def test_empty_when_not_my_turn(self, game):
        """No actions available when not our turn."""
        # End our turn
        if game.is_my_turn:
            game.game.end_turn()
        
        actions = game.get_valid_actions()
        assert len(actions) == 0
    
    def test_empty_when_game_over(self, game):
        """No actions when game is over."""
        from unittest.mock import patch, PropertyMock
        
        # Mock the game.ended property to return True
        with patch.object(type(game._game), 'ended', new_callable=PropertyMock) as mock_ended:
            mock_ended.return_value = True
            
            assert game.is_game_over
            actions = game.get_valid_actions()
            assert len(actions) == 0


class TestStep:
    """Tests for action execution."""
    
    @pytest.fixture
    def game(self):
        """Create a game ready to play."""
        from ai.game_wrapper import HearthstoneGame
        g = HearthstoneGame()
        g.reset()
        return g
    
    def test_step_returns_tuple(self, game):
        """Step should return (state, reward, done, info)."""
        from ai.actions import Action
        
        action = Action.end_turn()
        result = game.step(action)
        
        assert isinstance(result, tuple)
        assert len(result) == 4
    
    def test_step_end_turn_changes_player(self, game):
        """Ending turn should change current player."""
        from ai.actions import Action
        
        before = game.current_player
        action = Action.end_turn()
        game.step(action)
        
        assert game.current_player != before
    
    def test_step_increments_counter(self, game):
        """Each step should increment the step counter."""
        from ai.actions import Action
        
        before = game._step_count
        action = Action.end_turn()
        game.step(action)
        
        assert game._step_count == before + 1
    
    def test_reward_zero_during_game(self, game):
        """Reward should be 0 while game is ongoing."""
        from ai.actions import Action
        
        action = Action.end_turn()
        _, reward, done, _ = game.step(action)
        
        if not done:
            assert reward == 0.0


class TestActionMask:
    """Tests for action mask generation."""
    
    def test_mask_length(self):
        """Mask should have correct length."""
        from ai.game_wrapper import HearthstoneGame
        from ai.actions import ACTION_SPACE_SIZE
        
        game = HearthstoneGame()
        game.reset()
        
        mask = game.get_valid_action_mask()
        assert len(mask) == ACTION_SPACE_SIZE
    
    def test_mask_binary(self):
        """Mask should only contain 0 or 1."""
        from ai.game_wrapper import HearthstoneGame
        
        game = HearthstoneGame()
        game.reset()
        
        mask = game.get_valid_action_mask()
        assert all(m in [0, 1] for m in mask)
    
    def test_mask_matches_actions(self):
        """Valid actions should have 1 in mask."""
        from ai.game_wrapper import HearthstoneGame
        
        game = HearthstoneGame()
        game.reset()
        
        if game.is_my_turn:
            actions = game.get_valid_actions()
            mask = game.get_valid_action_mask()
            
            for action in actions:
                idx = action.to_index()
                assert mask[idx] == 1


class TestPlayRandomGame:
    """Tests for the random game function."""
    
    def test_completes_without_error(self):
        """Random game should complete without errors."""
        from ai.game_wrapper import play_random_game
        
        winner = play_random_game(verbose=False)
        assert winner in [0, 1, 2]
    
    def test_returns_winner(self):
        """Should return the winner ID."""
        from ai.game_wrapper import play_random_game
        
        winner = play_random_game(verbose=False)
        assert isinstance(winner, int)
