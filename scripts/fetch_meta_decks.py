#!/usr/bin/env python3
"""
HSReplay Meta Deck Fetcher

Fetches top archetypes from HSReplay and converts them to usable deck lists
for self-play training.
"""

import urllib.request
import json
import gzip
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MetaDeckFetcher:
    """Fetches and converts HSReplay archetype data."""
    
    ARCHETYPES_URL = "https://api.hsreplay.net/v1/archetypes/"
    HEARTHSTONE_JSON_URL = "https://api.hearthstonejson.com/v1/latest/enUS/cards.json"
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.dbf_map: Dict[int, Dict] = {}
        self.archetypes: List[Dict] = []
        
    def _fetch_json(self, url: str) -> Optional[dict]:
        """Fetch JSON from URL."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                try:
                    data = gzip.decompress(data)
                except:
                    pass
                return json.loads(data.decode('utf-8'))
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def load_or_fetch_dbf_map(self) -> bool:
        """Load DBF map from cache or fetch from HearthstoneJSON."""
        cache_path = self.data_dir / "dbf_map.json"
        
        if cache_path.exists():
            print("Loading DBF map from cache...")
            with open(cache_path) as f:
                # Keys are strings in JSON, convert to int
                raw = json.load(f)
                self.dbf_map = {int(k): v for k, v in raw.items()}
            print(f"  Loaded {len(self.dbf_map)} entries")
            return True
        
        print("Fetching card data from HearthstoneJSON...")
        cards = self._fetch_json(self.HEARTHSTONE_JSON_URL)
        
        if not cards:
            return False
        
        print(f"  Got {len(cards)} cards")
        
        for card in cards:
            dbf_id = card.get('dbfId')
            card_id = card.get('id')
            if dbf_id and card_id:
                self.dbf_map[dbf_id] = {
                    'id': card_id,
                    'name': card.get('name', ''),
                    'cost': card.get('cost', 0),
                    'type': card.get('type', ''),
                    'cardClass': card.get('cardClass', 'NEUTRAL'),
                }
        
        # Cache it
        with open(cache_path, 'w') as f:
            json.dump(self.dbf_map, f)
        print(f"  Cached {len(self.dbf_map)} entries")
        
        return True
    
    def fetch_archetypes(self) -> bool:
        """Fetch archetypes from HSReplay."""
        print("Fetching archetypes from HSReplay...")
        
        data = self._fetch_json(self.ARCHETYPES_URL)
        if not data:
            return False
        
        self.archetypes = data
        print(f"  Got {len(self.archetypes)} archetypes")
        
        # Cache it
        with open(self.data_dir / "archetypes.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    
    def get_archetype_cards(self, archetype: Dict, format_type: str = "standard") -> List[str]:
        """Extract card IDs from archetype signature."""
        sig_key = f"{format_type}_ccp_signature_core"
        sig = archetype.get(sig_key)
        
        if not sig or not sig.get('components'):
            return []
        
        card_ids = []
        for dbf_id in sig['components']:
            if dbf_id in self.dbf_map:
                card_ids.append(self.dbf_map[dbf_id]['id'])
        
        return card_ids
    
    def build_meta_decks(self, min_cards: int = 5) -> Dict[str, Dict]:
        """Build deck templates from top archetypes."""
        meta_decks = {}
        
        for arch in self.archetypes:
            name = arch.get('name', '')
            player_class = arch.get('player_class_name', 'NEUTRAL')
            
            if not name or player_class in ['NEUTRAL', 'WHIZBANG']:
                continue
            
            cards = self.get_archetype_cards(arch, "standard")
            if len(cards) < min_cards:
                # Try wild
                cards = self.get_archetype_cards(arch, "wild")
            
            if len(cards) >= min_cards:
                # Create a key like "DRUID_Token"
                key = f"{player_class}_{name.replace(' ', '_')}"
                meta_decks[key] = {
                    'name': name,
                    'class': player_class,
                    'archetype_id': arch.get('id'),
                    'signature_cards': cards,
                    'url': arch.get('url', ''),
                }
        
        return meta_decks
    
    def generate_deck_code(self, deck_info: Dict) -> List[str]:
        """
        Generate a full deck from signature cards.
        Fills remaining slots with class staples/neutrals.
        """
        cards = deck_info['signature_cards'].copy()
        
        # Duplicate each card (most decks run 2x)
        full_deck = []
        for card in cards:
            full_deck.append(card)
            if len(full_deck) < 30:
                full_deck.append(card)  # Add second copy
        
        return full_deck[:30]
    
    def save_meta_decks(self, output_file: str = "meta_decks.json"):
        """Save processed meta decks."""
        meta_decks = self.build_meta_decks()
        
        output_path = self.data_dir / output_file
        with open(output_path, 'w') as f:
            json.dump(meta_decks, f, indent=2)
        
        print(f"\nSaved {len(meta_decks)} meta decks to {output_path}")
        return meta_decks


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch HSReplay meta decks')
    parser.add_argument('--data-dir', default='data', help='Data directory')
    parser.add_argument('--refresh', action='store_true', help='Force refresh data')
    parser.add_argument('--list', action='store_true', help='List available archetypes')
    
    args = parser.parse_args()
    
    fetcher = MetaDeckFetcher(args.data_dir)
    
    # Load DBF map
    if not fetcher.load_or_fetch_dbf_map():
        print("Failed to load DBF map")
        sys.exit(1)
    
    # Fetch archetypes
    if not fetcher.fetch_archetypes():
        print("Failed to fetch archetypes")
        sys.exit(1)
    
    # Build and save meta decks
    meta_decks = fetcher.save_meta_decks()
    
    if args.list:
        print("\nAvailable archetypes by class:")
        by_class = {}
        for key, deck in meta_decks.items():
            cls = deck['class']
            if cls not in by_class:
                by_class[cls] = []
            by_class[cls].append((deck['name'], len(deck['signature_cards'])))
        
        for cls in sorted(by_class.keys()):
            print(f"\n{cls}:")
            for name, count in sorted(by_class[cls], key=lambda x: -x[1])[:10]:
                print(f"  {name} ({count} cards)")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total archetypes: {len(fetcher.archetypes)}")
    print(f"Usable meta decks: {len(meta_decks)}")
    
    # Show top decks per class
    print("\nTop archetypes (by signature card count):")
    sorted_decks = sorted(meta_decks.items(), key=lambda x: -len(x[1]['signature_cards']))
    for key, deck in sorted_decks[:15]:
        print(f"  {deck['class']:12} {deck['name']:30} ({len(deck['signature_cards'])} cards)")


if __name__ == '__main__':
    main()
