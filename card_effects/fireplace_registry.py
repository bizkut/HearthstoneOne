"""Master Card Effects Registry - Aggregates all Fireplace-ported effects.

This module provides a unified interface to access all ported card effects
across all expansions.
"""


def get_all_effects():
    """Get a combined dictionary of all ported card effects.
    
    Returns:
        Dict[str, Callable]: Card ID -> effect handler mapping
    """
    all_effects = {}
    
    # Classic
    try:
        from card_effects.classic import CLASSIC_EFFECTS
        all_effects.update(CLASSIC_EFFECTS)
    except ImportError:
        pass
    
    # Naxxramas
    try:
        from card_effects.naxx.naxx_effects import NAXX_EFFECTS
        all_effects.update(NAXX_EFFECTS)
    except ImportError:
        pass
    
    # GVG
    try:
        from card_effects.gvg.gvg_effects import GVG_EFFECTS
        all_effects.update(GVG_EFFECTS)
    except ImportError:
        pass
    
    # Blackrock Mountain
    try:
        from card_effects.brm.brm_effects import BRM_EFFECTS
        all_effects.update(BRM_EFFECTS)
    except ImportError:
        pass
    
    # League of Explorers
    try:
        from card_effects.loe.loe_effects import LOE_EFFECTS
        all_effects.update(LOE_EFFECTS)
    except ImportError:
        pass
    
    # The Grand Tournament
    try:
        from card_effects.tgt.tgt_effects import TGT_EFFECTS
        all_effects.update(TGT_EFFECTS)
    except ImportError:
        pass
    
    # Whispers of the Old Gods
    try:
        from card_effects.og.wog_effects import WOG_EFFECTS
        all_effects.update(WOG_EFFECTS)
    except ImportError:
        pass
    
    # Knights of the Frozen Throne
    try:
        from card_effects.icecrown.icc_effects import ICC_EFFECTS
        all_effects.update(ICC_EFFECTS)
    except ImportError:
        pass
    
    # Kobolds and Catacombs
    try:
        from card_effects.lootapalooza.kobolds_effects import KOBOLDS_EFFECTS
        all_effects.update(KOBOLDS_EFFECTS)
    except ImportError:
        pass
    
    # The Witchwood
    try:
        from card_effects.gilneas.witchwood_effects import WITCHWOOD_EFFECTS
        all_effects.update(WITCHWOOD_EFFECTS)
    except ImportError:
        pass
    
    # The Boomsday Project
    try:
        from card_effects.boomsday.boomsday_effects import BOOMSDAY_EFFECTS
        all_effects.update(BOOMSDAY_EFFECTS)
    except ImportError:
        pass
    
    # Rastakhan's Rumble
    try:
        from card_effects.troll.rastakhan_effects import RASTAKHAN_EFFECTS
        all_effects.update(RASTAKHAN_EFFECTS)
    except ImportError:
        pass
    
    # Rise of Shadows
    try:
        from card_effects.dalaran.dalaran_effects import DALARAN_EFFECTS
        all_effects.update(DALARAN_EFFECTS)
    except ImportError:
        pass
    
    # Saviors of Uldum
    try:
        from card_effects.uldum.uldum_effects import ULDUM_EFFECTS
        all_effects.update(ULDUM_EFFECTS)
    except ImportError:
        pass
    
    # Descent of Dragons
    try:
        from card_effects.dragons.dragons_effects import DRAGONS_EFFECTS
        all_effects.update(DRAGONS_EFFECTS)
    except ImportError:
        pass
    
    # Ashes of Outland
    try:
        from card_effects.outlands.outlands_effects import OUTLANDS_EFFECTS
        all_effects.update(OUTLANDS_EFFECTS)
    except ImportError:
        pass
    
    return all_effects


def get_effect_count():
    """Get the total count of ported effects."""
    return len(get_all_effects())


def get_effect(card_id: str):
    """Get the effect handler for a specific card.
    
    Args:
        card_id: The card's ID (e.g., "CS2_029" for Fireball)
        
    Returns:
        The effect handler function, or None if not found
    """
    effects = get_all_effects()
    return effects.get(card_id)


def register_all_effects(game) -> int:
    """Register all Fireplace-ported effects with a game instance.
    
    Args:
        game: The game instance to register effects with
        
    Returns:
        Number of effects registered
    """
    effects = get_all_effects()
    count = 0
    for card_id, handler in effects.items():
        if hasattr(game, '_battlecry_handlers'):
            game._battlecry_handlers[card_id] = handler
            count += 1
    return count


# Print stats when loaded
if __name__ == "__main__":
    print(f"Total Fireplace-ported effects: {get_effect_count()}")
