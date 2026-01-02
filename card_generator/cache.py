"""Card Effect Cache.

Manages saving and loading of generated card effects, organized by expansion.
"""

import os
import importlib.util
from typing import Optional, Callable, Dict

class EffectCache:
    """Manages the storage and retrieval of generated Python code for card effects."""
    
    def __init__(self, cache_dir: str = "card_effects"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            # Create __init__.py to make it a package
            with open(os.path.join(cache_dir, "__init__.py"), "w") as f:
                f.write('"""Generated card effects."""\n')

    def get_expansion_dir(self, card_set: str) -> str:
        """Returns the directory path for a specific expansion."""
        # Sanitize card_set for directory name
        dir_name = card_set.lower().replace(" ", "_")
        expansion_dir = os.path.join(self.cache_dir, dir_name)
        if not os.path.exists(expansion_dir):
            os.makedirs(expansion_dir, exist_ok=True)
            with open(os.path.join(expansion_dir, "__init__.py"), "w") as f:
                f.write(f'"""Generated effects for {card_set}."""\n')
        return expansion_dir

    def get_effect_path(self, card_id: str, card_set: Optional[str] = None) -> str:
        """Returns the file path for a card's effect code."""
        if card_set:
            expansion_dir = self.get_expansion_dir(card_set)
            return os.path.join(expansion_dir, f"effect_{card_id}.py")
        
        # Fallback search if card_set not provided
        for entry in os.listdir(self.cache_dir):
            full_path = os.path.join(self.cache_dir, entry)
            if os.path.isdir(full_path):
                effect_path = os.path.join(full_path, f"effect_{card_id}.py")
                if os.path.exists(effect_path):
                    return effect_path
                    
        return os.path.join(self.cache_dir, f"effect_{card_id}.py")

    def is_cached(self, card_id: str, card_set: Optional[str] = None) -> bool:
        """Checks if the effect code for a card exists in the cache."""
        path = self.get_effect_path(card_id, card_set)
        return os.path.exists(path)

    def save_effect(self, card_id: str, code: str, card_set: str = "LEGACY") -> bool:
        """Saves the generated Python code to the cache."""
        try:
            path = self.get_effect_path(card_id, card_set)
            with open(path, "w", encoding="utf-8") as f:
                f.write(f'"""Effect for {card_id} in {card_set}"""\n\n')
                f.write(code)
            return True
        except Exception as e:
            print(f"Error saving effect: {e}")
            return False

    def load_effect(self, card_id: str, card_set: Optional[str] = None) -> Optional[Dict[str, Callable]]:
        """Loads the effect functions from the cache."""
        path = self.get_effect_path(card_id, card_set)
        if not os.path.exists(path):
            return None

        try:
            # We need to calculate the correct module path
            # Assuming card_effects is in the PYTHONPATH
            rel_path = os.path.relpath(path, os.path.dirname(self.cache_dir))
            module_name = rel_path.replace(os.sep, ".").replace(".py", "")
            
            spec = importlib.util.spec_from_file_location(f"effect_{card_id}", path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                
                # Dynamic imports to avoid circular dependency
                from simulator.card_loader import create_card, CardDatabase
                module.__dict__["create_card"] = create_card
                module.__dict__["CardDatabase"] = CardDatabase
                
                spec.loader.exec_module(module)
                
                effects = {}
                for attr in ["battlecry", "deathrattle", "on_play", "setup"]:
                    if hasattr(module, attr):
                        effects[attr] = getattr(module, attr)
                
                return effects
            return None
        except Exception as e:
            print(f"Error loading effect for {card_id}: {e}")
            return None
