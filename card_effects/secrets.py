"""Secrets System and Common Secret Effects.

This module implements the secret trigger system and common secrets from:
- Mage (Counterspell, Ice Block, Mirror Entity, etc.)
- Hunter (Explosive Trap, Freezing Trap, etc.)
- Paladin (Noble Sacrifice, Redemption, etc.)
- Rogue (Evasion, etc.)
"""

import random
from typing import Optional, Callable, Dict, List


# === SECRET TRIGGER TYPES ===
# Secrets trigger on specific events

SECRET_TRIGGERS = {
    # Mage
    "EX1_287": "on_spell_played",      # Counterspell
    "EX1_289": "on_spell_targeted",    # Ice Barrier
    "EX1_294": "on_minion_played",     # Mirror Entity
    "EX1_295": "on_hero_attacked",     # Ice Block
    "tt_010": "on_minion_attack",      # Spellbender
    "EX1_533": "on_turn_end",          # Mana Bind
    
    # Hunter
    "EX1_610": "on_hero_attacked",     # Explosive Trap
    "EX1_611": "on_minion_attack",     # Freezing Trap
    "EX1_554": "on_minion_attack",     # Snake Trap
    "EX1_609": "on_minion_played",     # Snipe
    "EX1_536": "on_minion_attack",     # Misdirection
    "KAR_004": "on_spell_played",      # Cat Trick
    
    # Paladin
    "EX1_130": "on_minion_attack",     # Noble Sacrifice
    "EX1_136": "on_friendly_die",      # Redemption
    "EX1_379": "on_friendly_die",      # Repentance (actually on_minion_played)
    "FP1_020": "on_friendly_die",      # Avenge
    
    # Rogue
    "LOOT_204": "on_hero_attacked",    # Evasion
}


# === MAGE SECRETS ===

def secret_EX1_287(game, source, event_data):
    """Counterspell: When your opponent casts a spell, Counter it."""
    spell = event_data.get('card')
    if spell:
        # Counter the spell (prevent it from resolving)
        event_data['countered'] = True
        return True  # Secret triggered
    return False


def secret_EX1_289(game, source, event_data):
    """Ice Barrier: When your hero is attacked, gain 8 Armor."""
    if source.controller.hero:
        source.controller.hero.gain_armor(8)
    return True


def secret_EX1_294(game, source, event_data):
    """Mirror Entity: When your opponent plays a minion, summon a copy of it."""
    minion = event_data.get('card')
    if minion and len(source.controller.board) < 7:
        game.summon_token(source.controller, minion.card_id)
    return True


def secret_EX1_295(game, source, event_data):
    """Ice Block: When your hero takes fatal damage, prevent it and become Immune this turn."""
    hero = source.controller.hero
    if hero:
        # Check if damage would be fatal
        damage = event_data.get('damage', 0)
        if hero.health - damage <= 0:
            event_data['prevented'] = True
            hero.immune = True
            return True
    return False


# === HUNTER SECRETS ===

def secret_EX1_610(game, source, event_data):
    """Explosive Trap: When your hero is attacked, deal 2 damage to all enemies."""
    opponent = source.controller.opponent
    for minion in opponent.board[:]:
        game.deal_damage(minion, 2)
    if opponent.hero:
        game.deal_damage(opponent.hero, 2)
    return True


def secret_EX1_611(game, source, event_data):
    """Freezing Trap: When an enemy minion attacks, return it to its owner's hand. It costs (2) more."""
    attacker = event_data.get('attacker')
    if attacker and attacker.card_type.name == 'MINION':
        # Return to hand
        if attacker in attacker.controller.board:
            attacker.controller.board.remove(attacker)
            attacker._cost += 2
            attacker.controller.add_to_hand(attacker)
        return True
    return False


def secret_EX1_554(game, source, event_data):
    """Snake Trap: When one of your minions is attacked, summon three 1/1 Snakes."""
    for _ in range(3):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "EX1_554t")
    return True


def secret_EX1_609(game, source, event_data):
    """Snipe: When your opponent plays a minion, deal 4 damage to it."""
    minion = event_data.get('card')
    if minion:
        game.deal_damage(minion, 4)
    return True


# === PALADIN SECRETS ===

def secret_EX1_130(game, source, event_data):
    """Noble Sacrifice: When an enemy attacks, summon a 2/1 Defender as the new target."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "EX1_130a")
        # Redirect attack to the Defender
        event_data['new_target'] = source.controller.board[-1]
    return True


def secret_EX1_136(game, source, event_data):
    """Redemption: When a friendly minion dies, return it to life with 1 Health."""
    minion = event_data.get('minion')
    if minion and len(source.controller.board) < 7:
        game.summon_token(source.controller, minion.card_id)
        # Set to 1 health
        summoned = source.controller.board[-1]
        summoned._damage = summoned.max_health - 1
    return True


def secret_FP1_020(game, source, event_data):
    """Avenge: When one of your minions dies, give a random friendly minion +3/+2."""
    friendly_minions = [m for m in source.controller.board]
    if friendly_minions:
        chosen = random.choice(friendly_minions)
        chosen._attack += 3
        chosen._health += 2
        chosen.max_health += 2
    return True


# === ROGUE SECRETS ===

def secret_LOOT_204(game, source, event_data):
    """Evasion: When your hero takes damage, become Immune this turn."""
    if source.controller.hero:
        source.controller.hero.immune = True
    return True


# Secret handlers registry
SECRET_HANDLERS: Dict[str, Callable] = {
    # Mage
    "EX1_287": secret_EX1_287,  # Counterspell
    "EX1_289": secret_EX1_289,  # Ice Barrier
    "EX1_294": secret_EX1_294,  # Mirror Entity
    "EX1_295": secret_EX1_295,  # Ice Block
    # Hunter
    "EX1_610": secret_EX1_610,  # Explosive Trap
    "EX1_611": secret_EX1_611,  # Freezing Trap
    "EX1_554": secret_EX1_554,  # Snake Trap
    "EX1_609": secret_EX1_609,  # Snipe
    # Paladin
    "EX1_130": secret_EX1_130,  # Noble Sacrifice
    "EX1_136": secret_EX1_136,  # Redemption
    "FP1_020": secret_FP1_020,  # Avenge
    # Rogue
    "LOOT_204": secret_LOOT_204,  # Evasion
}


def get_secret_handler(card_id: str) -> Optional[Callable]:
    """Get the handler for a secret."""
    return SECRET_HANDLERS.get(card_id)


def get_secret_trigger(card_id: str) -> Optional[str]:
    """Get the trigger event type for a secret."""
    return SECRET_TRIGGERS.get(card_id)


def check_secrets(game, trigger_type: str, event_data: dict) -> None:
    """Check and trigger any secrets that match the event.
    
    Args:
        game: The game instance
        trigger_type: The type of event (e.g., 'on_spell_played')
        event_data: Event-specific data (e.g., the spell card)
    """
    # Check opponent's secrets (secrets trigger on opponent's turn)
    current_player = game.current_player
    opponent = current_player.opponent if current_player else None
    
    if not opponent:
        return
    
    secrets_to_remove = []
    
    for secret in opponent.secrets[:]:
        secret_id = secret.card_id
        if SECRET_TRIGGERS.get(secret_id) == trigger_type:
            handler = SECRET_HANDLERS.get(secret_id)
            if handler and handler(game, secret, event_data):
                secrets_to_remove.append(secret)
                break  # Only one secret triggers per event
    
    # Remove triggered secrets
    for secret in secrets_to_remove:
        opponent.secrets.remove(secret)
