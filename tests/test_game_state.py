"""Tests for game state and data structures."""

import pytest


class TestCardInfo:
    """Tests for CardInfo dataclass."""
    
    def test_creation(self):
        """CardInfo can be created with required fields."""
        from ai.card import CardInfo, CardType
        
        card = CardInfo(
            card_id="CS2_029",
            name="Fireball",
            card_type=CardType.SPELL,
            cost=4,
        )
        
        assert card.card_id == "CS2_029"
        assert card.name == "Fireball"
        assert card.cost == 4
    
    def test_is_minion(self):
        """is_minion returns True for minions."""
        from ai.card import CardInfo, CardType
        
        minion = CardInfo("CS2_182", "Yeti", CardType.MINION, 4, attack=4, health=5)
        spell = CardInfo("CS2_029", "Fireball", CardType.SPELL, 4)
        
        assert minion.is_minion()
        assert not spell.is_minion()
    
    def test_is_spell(self):
        """is_spell returns True for spells."""
        from ai.card import CardInfo, CardType
        
        spell = CardInfo("CS2_029", "Fireball", CardType.SPELL, 4)
        minion = CardInfo("CS2_182", "Yeti", CardType.MINION, 4)
        
        assert spell.is_spell()
        assert not minion.is_spell()
    
    def test_immutable(self):
        """CardInfo should be immutable (frozen)."""
        from ai.card import CardInfo, CardType
        
        card = CardInfo("CS2_029", "Fireball", CardType.SPELL, 4)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            card.cost = 5


class TestCardInstance:
    """Tests for CardInstance class."""
    
    def test_to_dict(self):
        """to_dict returns proper dictionary."""
        from ai.card import CardInfo, CardInstance, CardType
        
        info = CardInfo("CS2_182", "Yeti", CardType.MINION, 4, attack=4, health=5)
        instance = CardInstance(
            info=info,
            current_cost=4,
            current_attack=4,
            current_health=5,
            max_health=5,
        )
        
        d = instance.to_dict()
        
        assert d["card_id"] == "CS2_182"
        assert d["name"] == "Yeti"
        assert d["type"] == "MINION"
        assert d["current_cost"] == 4
        assert d["attack"] == 4
        assert d["health"] == 5


class TestPlayerState:
    """Tests for PlayerState class."""
    
    def test_to_dict(self):
        """to_dict returns proper structure."""
        from ai.player import PlayerState, HeroState
        
        hero = HeroState(health=30)
        player = PlayerState(
            player_id=1,
            hero=hero,
            mana=5,
            max_mana=5,
        )
        
        d = player.to_dict()
        
        assert d["player_id"] == 1
        assert d["mana"] == 5
        assert d["hero"]["health"] == 30
        assert "hand" in d
        assert "board" in d


class TestHeroState:
    """Tests for HeroState class."""
    
    def test_effective_health(self):
        """effective_health includes armor."""
        from ai.player import HeroState
        
        hero = HeroState(health=20, armor=5)
        assert hero.effective_health == 25
    
    def test_effective_health_no_armor(self):
        """effective_health works without armor."""
        from ai.player import HeroState
        
        hero = HeroState(health=30)
        assert hero.effective_health == 30


class TestGameState:
    """Tests for GameState class."""
    
    def test_board_property(self):
        """board property returns BoardState."""
        from ai.game_state import GameState, BoardState
        from ai.player import PlayerState, HeroState
        
        hero = HeroState(health=30)
        p1 = PlayerState(1, hero, 0, 0)
        p2 = PlayerState(2, hero, 0, 0)
        
        state = GameState(
            turn=1,
            current_player=1,
            friendly_player=p1,
            enemy_player=p2,
        )
        
        assert isinstance(state.board, BoardState)
    
    def test_is_my_turn(self):
        """is_my_turn works correctly."""
        from ai.game_state import GameState
        from ai.player import PlayerState, HeroState
        
        hero = HeroState(health=30)
        p1 = PlayerState(1, hero, 0, 0)
        p2 = PlayerState(2, hero, 0, 0)
        
        state1 = GameState(turn=1, current_player=1, friendly_player=p1, enemy_player=p2)
        state2 = GameState(turn=1, current_player=2, friendly_player=p1, enemy_player=p2)
        
        assert state1.is_my_turn
        assert not state2.is_my_turn
    
    def test_to_dict(self):
        """to_dict returns complete structure."""
        from ai.game_state import GameState
        from ai.player import PlayerState, HeroState
        
        hero = HeroState(health=30)
        p1 = PlayerState(1, hero, 5, 5)
        p2 = PlayerState(2, hero, 0, 5)
        
        state = GameState(
            turn=5,
            current_player=1,
            friendly_player=p1,
            enemy_player=p2,
        )
        
        d = state.to_dict()
        
        assert d["turn"] == 5
        assert d["current_player"] == 1
        assert "friendly" in d
        assert "enemy" in d


class TestAction:
    """Tests for Action class."""
    
    def test_end_turn(self):
        """end_turn creates correct action."""
        from ai.actions import Action, ActionType
        
        action = Action.end_turn()
        assert action.action_type == ActionType.END_TURN
    
    def test_play_card(self):
        """play_card creates correct action."""
        from ai.actions import Action, ActionType
        
        action = Action.play_card(0, target_index=2)
        
        assert action.action_type == ActionType.PLAY_CARD
        assert action.card_index == 0
        assert action.target_index == 2
    
    def test_attack(self):
        """attack creates correct action."""
        from ai.actions import Action, ActionType
        
        action = Action.attack(0, -1)  # Minion 0 attacks enemy hero
        
        assert action.action_type == ActionType.ATTACK
        assert action.attacker_index == 0
        assert action.target_index == -1
    
    def test_hero_power(self):
        """hero_power creates correct action."""
        from ai.actions import Action, ActionType
        
        action = Action.hero_power()
        assert action.action_type == ActionType.HERO_POWER
    
    def test_to_index_end_turn(self):
        """END_TURN maps to index 0."""
        from ai.actions import Action
        
        action = Action.end_turn()
        assert action.to_index() == 0
    
    def test_from_index_end_turn(self):
        """Index 0 maps to END_TURN."""
        from ai.actions import Action, ActionType
        
        action = Action.from_index(0)
        assert action.action_type == ActionType.END_TURN
    
    def test_index_roundtrip(self):
        """to_index and from_index are inverses."""
        from ai.actions import Action, ActionType
        
        actions = [
            Action.end_turn(),
            Action.hero_power(),
            Action.play_card(0),
            Action.play_card(2, target_index=1),
            Action.attack(0, -1),
            Action.attack(2, 1),
        ]
        
        for action in actions:
            idx = action.to_index()
            recovered = Action.from_index(idx)
            assert recovered.action_type == action.action_type
    
    def test_repr(self):
        """__repr__ returns readable string."""
        from ai.actions import Action
        
        action = Action.end_turn()
        repr_str = repr(action)
        assert "END_TURN" in repr_str
