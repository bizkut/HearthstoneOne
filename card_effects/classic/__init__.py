"""Classic Card Effects Registry.

Aggregates all ported Classic/EXPERT1 card effects from Fireplace.
"""

from .mage_spells import MAGE_SPELL_EFFECTS
from .neutral_effects import NEUTRAL_EFFECTS
from .multiclass_spells import MULTICLASS_EFFECTS


# Combined registry of all Classic effects
CLASSIC_EFFECTS = {}
CLASSIC_EFFECTS.update(MAGE_SPELL_EFFECTS)
CLASSIC_EFFECTS.update(NEUTRAL_EFFECTS)
CLASSIC_EFFECTS.update(MULTICLASS_EFFECTS)


def get_classic_effect(card_id: str):
    """Get the effect handler for a Classic card."""
    return CLASSIC_EFFECTS.get(card_id)


def register_classic_effects(game) -> int:
    """Register all Classic effects with a game instance.
    
    Returns:
        Number of effects registered
    """
    count = 0
    for card_id, handler in CLASSIC_EFFECTS.items():
        game._battlecry_handlers[card_id] = handler
        count += 1
    return count


# Stats
TOTAL_CLASSIC_EFFECTS = len(CLASSIC_EFFECTS)
