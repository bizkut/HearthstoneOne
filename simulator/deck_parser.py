"""Deck String Parser for HearthstoneOne.

Parse Blizzard deck codes (e.g., 'AAEBAf0...') into card lists.
Uses python-hearthstone library for deckstring parsing.
"""

import base64
from io import BytesIO
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass


# Deckstring version
DECKSTRING_VERSION = 1


@dataclass
class DeckInfo:
    """Parsed deck information."""
    hero_dbf_id: int
    format_type: int  # 1=Wild, 2=Standard
    cards: List[Tuple[int, int]]  # List of (dbf_id, count)
    
    @property
    def card_count(self) -> int:
        return sum(count for _, count in self.cards)


def _read_varint(stream: BytesIO) -> int:
    """Read a variable-length integer from stream."""
    shift = 0
    result = 0
    while True:
        c = stream.read(1)
        if c == b"":
            raise EOFError("Unexpected EOF while reading varint")
        i = ord(c)
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            break
    return result


def parse_deckstring(deckstring: str) -> DeckInfo:
    """Parse a Blizzard deckstring into card list.
    
    Args:
        deckstring: Base64 encoded deck string (e.g., 'AAEBAf0GBO0E...')
        
    Returns:
        DeckInfo with hero, format, and card list
        
    Example:
        >>> deck = parse_deckstring("AAEBAf0EBu0F...")
        >>> print(deck.cards)  # [(1234, 2), (5678, 1), ...]
    """
    decoded = base64.b64decode(deckstring)
    data = BytesIO(decoded)

    # Header
    if data.read(1) != b"\0":
        raise ValueError("Invalid deckstring")

    version = _read_varint(data)
    if version != DECKSTRING_VERSION:
        raise ValueError(f"Unsupported deckstring version {version}")

    format_type = _read_varint(data)

    # Heroes
    num_heroes = _read_varint(data)
    heroes = []
    for _ in range(num_heroes):
        heroes.append(_read_varint(data))
    
    hero_dbf_id = heroes[0] if heroes else 0

    # Cards
    cards: List[Tuple[int, int]] = []

    # Single copy cards
    num_cards_x1 = _read_varint(data)
    for _ in range(num_cards_x1):
        card_id = _read_varint(data)
        cards.append((card_id, 1))

    # Double copy cards
    num_cards_x2 = _read_varint(data)
    for _ in range(num_cards_x2):
        card_id = _read_varint(data)
        cards.append((card_id, 2))

    # N-copy cards (for special cases)
    num_cards_xn = _read_varint(data)
    for _ in range(num_cards_xn):
        card_id = _read_varint(data)
        count = _read_varint(data)
        cards.append((card_id, count))

    cards.sort()

    return DeckInfo(
        hero_dbf_id=hero_dbf_id,
        format_type=format_type,
        cards=cards
    )


def load_deck_from_string(game, player, deckstring: str) -> bool:
    """Load a deck from deckstring into a player's deck.
    
    Args:
        game: Game instance
        player: Player to load deck for
        deckstring: Blizzard deck code
        
    Returns:
        True if successful, False otherwise
    """
    from .card_loader import CardDatabase, create_card
    
    try:
        deck_info = parse_deckstring(deckstring)
    except Exception as e:
        print(f"Failed to parse deckstring: {e}")
        return False
    
    db = CardDatabase.get_instance()
    db.load()
    
    # Build reverse lookup: dbf_id -> card_id
    dbf_to_card_id: Dict[int, str] = {}
    for card_id, card_data in db._cards.items():
        if hasattr(card_data, 'dbf_id'):
            dbf_to_card_id[card_data.dbf_id] = card_id
    
    # Clear existing deck
    player.deck.clear()
    
    # Load cards
    loaded = 0
    for dbf_id, count in deck_info.cards:
        card_id = dbf_to_card_id.get(dbf_id)
        if card_id:
            for _ in range(count):
                card = create_card(card_id, game)
                if card:
                    card.controller = player
                    player.deck.append(card)
                    loaded += 1
    
    player.shuffle_deck()
    print(f"Loaded {loaded}/{deck_info.card_count} cards from deck code")
    return loaded > 0


# Sample meta deck codes for training
SAMPLE_DECKS = {
    # Classic decks (simplified examples)
    "zoolock": "AAEBAf0GApMB8gUOzQHbBs4H9QfCCO0Tg64CvLYCt7wC980C/dACiNIDiNUDAAAA",
    "aggro_hunter": "AAECAR8C5e0C4eMCDo0BqAK1A8UD/gybhQP4sQObzQP61QOAAAAAAAAAAAAAAA==",
}


if __name__ == "__main__":
    # Test parsing
    test_deck = "AAEBAf0EBu0F7QSODqirAuCsAoS2AgyKAcABuwKLA6sEtASOtgKptwLrugLBwQLaxQKbywIA"
    try:
        deck = parse_deckstring(test_deck)
        print(f"Hero DBF ID: {deck.hero_dbf_id}")
        print(f"Format: {deck.format_type}")
        print(f"Cards: {len(deck.cards)} unique, {deck.card_count} total")
        for dbf_id, count in deck.cards[:5]:
            print(f"  - DBF {dbf_id}: x{count}")
    except Exception as e:
        print(f"Parse error: {e}")
