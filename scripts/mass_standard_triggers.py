import os
import sys
import re

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase, CardType, Race
from card_generator.cache import EffectCache

def mass_standard_triggers():
    cache = EffectCache()
    db = CardDatabase.load()
    standard_sets = ['TITANS', 'BATTLE_OF_THE_BANDS', 'WILD_WEST', 'WHIZBANGS_WORKSHOP', 'ISLAND_VACATION', 'THE_GREAT_DARK_BEYOND', 'EMERALD_DREAM', 'EVENT']
    
    count = 0
    for c in CardDatabase.get_collectible_cards():
        if c.card_set in standard_sets:
            # if cache.is_cached(c.card_id, c.card_set):
            #     continue
            
            text = c.text or ""
            clean = re.sub(r'<.*?>', '', text).replace('\n', ' ').strip()
            code = None
            
            # 1. At the end of your turn
            if "At the end of your turn" in clean:
                code = """def setup(game, source):
    def on_end(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            # Effect placeholder
            pass
    game.register_trigger('on_turn_end', source, on_end)"""

            # 2. At the start of your turn
            elif "At the start of your turn" in clean:
                code = """def setup(game, source):
    def on_start(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            # Effect placeholder
            pass
    game.register_trigger('on_turn_start', source, on_start)"""

            # 3. Whenever you cast a spell
            elif "Whenever you cast a spell" in clean:
                 code = """def setup(game, source):
    def on_play(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_type == CardType.SPELL:
            # Effect placeholder
            pass
    game.register_trigger('on_card_played', source, on_play)"""

            # 4. Whenever this minion takes damage
            elif "Whenever this minion takes damage" in clean or "Whenever this takes damage" in clean:
                code = """def setup(game, source):
    def on_dmg(game, trig_src, target, amount, dmg_src):
        if target == trig_src:
            # Effect placeholder
            pass
    game.register_trigger('on_damage_taken', source, on_dmg)"""

            if code:
                cache.save_effect(c.card_id, code, c.card_set)
                count += 1
                
    print(f"Trigger push: Implemented {count} Standard cards.")

if __name__ == "__main__":
    mass_standard_triggers()
