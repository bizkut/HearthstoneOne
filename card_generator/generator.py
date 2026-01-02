"""Card Effect Generator.

Prepares prompts for LLM and handles the generation of Python code for card effects.
"""

from typing import Optional, Dict, Any
from simulator import CardData
from .cache import EffectCache

class EffectGenerator:
    """System to generate Python code for Hearthstone card effects using LLM."""
    
    def __init__(self, cache: Optional[EffectCache] = None):
        self.cache = cache or EffectCache()
        
    def generate_prompt(self, card: CardData) -> str:
        """Creates a detailed prompt for the LLM to generate code for a card."""
        prompt = f"""
You are a Hearthstone card effect implementation expert.
Your task is to write Python code for the following card:

Name: {card.name}
ID: {card.card_id}
Type: {card.card_type.name}
Text: {card.text}
Stats: {card.attack}/{card.health} (Cost: {card.cost})

Rules:
1. Use the provided Game and Entity API.
2. The code MUST contain one or more of these functions:
   - `def battlecry(game, source, target):`
   - `def deathrattle(game, source):`
   - `def on_play(game, source, target):` (for spells)
   - `def setup(game, source):` (to register persistent triggers)

API available:
- `game.deal_damage(target, amount, source)`
- `game.heal(target, amount)`
- `game.summon_token(player, card_id, position)`
- `game.register_trigger(event_name, source, callback)`
- `game.initiate_discover(player, options, callback)`
- Events: 'on_turn_start', 'on_turn_end', 'on_minion_summon', 'on_minion_death', 'on_damage_taken', 'on_card_played'
- `source.controller`, `source.controller.opponent`
- Trackers: `controller.spells_played_this_game` (list), `controller.dead_minions` (list), `controller.damage_taken_this_turn` (int), `controller.cards_drawn_this_game` (list)

Provide ONLY the Python code, no explanation.

Example for Rewind (ETC_531):
def on_play(game, source, target):
    player = source.controller
    options = list(set(player.spells_played_this_game))[-3:]
    def on_choose(game, card_id):
        game.current_player.add_to_hand(create_card(card_id, game))
    game.initiate_discover(player, options, on_choose)
"""
        return prompt

    def implement_manually(self, card_id: str, code: str, card_set: str = "LEGACY"):
        """Allows direct insertion of code into the cache (useful for the AI agent itself)."""
        self.cache.save_effect(card_id, code, card_set)
        print(f"Effect for {card_id} saved to cache ({card_set}).")
