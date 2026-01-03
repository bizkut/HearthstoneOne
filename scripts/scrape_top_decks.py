#!/usr/bin/env python3
"""
Top Meta Deck Scraper

Scrapes proven legend-ranked decks from hearthstone-decks.net,
decodes deck codes into card lists for training.
"""

import urllib.request
import re
import json
import base64
import struct
import os
import sys
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DeckCodeDecoder:
    """Decodes Hearthstone deck codes (AAE format) into card DBF IDs."""
    
    @staticmethod
    def decode(deck_code: str) -> Optional[Dict]:
        """
        Decode a deck code into its components.
        
        Returns:
            {
                'format': 1 (wild) or 2 (standard),
                'hero_dbf': int,
                'single_cards': [dbf_ids],
                'double_cards': [dbf_ids],
                'n_cards': [(dbf_id, count), ...]
            }
        """
        try:
            # Remove whitespace and decode base64
            code = deck_code.strip()
            data = base64.b64decode(code)
            
            offset = 0
            
            def read_varint():
                nonlocal offset
                result = 0
                shift = 0
                while True:
                    byte = data[offset]
                    offset += 1
                    result |= (byte & 0x7F) << shift
                    if not (byte & 0x80):
                        break
                    shift += 7
                return result
            
            # Skip reserved byte
            offset += 1
            
            # Version
            version = read_varint()
            
            # Format (1=Wild, 2=Standard)
            format_type = read_varint()
            
            # Number of heroes (usually 1)
            num_heroes = read_varint()
            hero_dbf = read_varint() if num_heroes > 0 else 0
            
            # Single copy cards
            num_singles = read_varint()
            singles = [read_varint() for _ in range(num_singles)]
            
            # Double copy cards  
            num_doubles = read_varint()
            doubles = [read_varint() for _ in range(num_doubles)]
            
            # N-copy cards (for special formats)
            n_cards = []
            if offset < len(data):
                num_n = read_varint()
                for _ in range(num_n):
                    dbf = read_varint()
                    count = read_varint()
                    n_cards.append((dbf, count))
            
            return {
                'format': format_type,
                'hero_dbf': hero_dbf,
                'single_cards': singles,
                'double_cards': doubles,
                'n_cards': n_cards
            }
            
        except Exception as e:
            print(f"Decode error: {e}")
            return None
    
    @staticmethod
    def get_all_cards(decoded: Dict) -> List[Tuple[int, int]]:
        """Get all cards as (dbf_id, count) pairs."""
        cards = []
        for dbf in decoded['single_cards']:
            cards.append((dbf, 1))
        for dbf in decoded['double_cards']:
            cards.append((dbf, 2))
        for dbf, count in decoded['n_cards']:
            cards.append((dbf, count))
        return cards


class MetaDeckScraper:
    """Scrapes top meta decks from hearthstone-decks.net"""
    
    BASE_URL = "https://hearthstone-decks.net"
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        }
        self.dbf_map: Dict[int, Dict] = {}
        
    def _fetch(self, url: str) -> Optional[str]:
        """Fetch URL content."""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode('utf-8')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def load_dbf_map(self) -> bool:
        """Load DBF ID to card ID mapping."""
        cache = self.data_dir / "dbf_map.json"
        if cache.exists():
            with open(cache) as f:
                raw = json.load(f)
                self.dbf_map = {int(k): v for k, v in raw.items()}
            return True
        print("DBF map not found. Run fetch_meta_decks.py first.")
        return False
    
    def get_deck_urls(self, limit: int = 50) -> List[str]:
        """Get deck page URLs from listing."""
        print("Finding deck URLs from hearthstone-decks.net...")
        content = self._fetch(f"{self.BASE_URL}/standard-decks/")
        
        if not content:
            return []
        
        # Find legend deck URLs
        urls = re.findall(
            r'href="(https://hearthstone-decks\.net/[a-z0-9-]+-(?:legend|top)[^"]+)"',
            content
        )
        unique = list(dict.fromkeys(urls))  # Deduplicate preserving order
        print(f"  Found {len(unique)} deck URLs")
        return unique[:limit]
    
    def scrape_deck(self, url: str) -> Optional[Dict]:
        """Scrape a single deck page."""
        content = self._fetch(url)
        if not content:
            return None
        
        # Extract deck code
        codes = re.findall(r'(AAE[A-Za-z0-9+/=]{30,})', content)
        if not codes:
            return None
        
        # Extract title
        title_match = re.search(r'<title>([^<]+)</title>', content)
        title = title_match.group(1).split(' - ')[0].strip() if title_match else 'Unknown'
        
        # Extract class from URL
        class_patterns = [
            'death-knight', 'demon-hunter', 'druid', 'hunter', 'mage',
            'paladin', 'priest', 'rogue', 'shaman', 'warlock', 'warrior'
        ]
        deck_class = 'UNKNOWN'
        for cls in class_patterns:
            if cls in url.lower():
                deck_class = cls.upper().replace('-', '')
                break
        
        # Decode the deck
        decoded = DeckCodeDecoder.decode(codes[0])
        if not decoded:
            return None
        
        # Convert DBF IDs to card IDs
        card_list = []
        for dbf, count in DeckCodeDecoder.get_all_cards(decoded):
            if dbf in self.dbf_map:
                card_info = self.dbf_map[dbf]
                for _ in range(count):
                    card_list.append(card_info['id'])
        
        return {
            'name': title,
            'class': deck_class,
            'url': url,
            'code': codes[0],
            'format': 'STANDARD' if decoded['format'] == 2 else 'WILD',
            'cards': card_list,
            'card_count': len(card_list)
        }
    
    def scrape_top_decks(self, limit: int = 30) -> List[Dict]:
        """Scrape top meta decks."""
        if not self.load_dbf_map():
            return []
        
        urls = self.get_deck_urls(limit)
        decks = []
        
        for i, url in enumerate(urls):
            short_name = url.split('/')[-2][:40]
            print(f"[{i+1}/{len(urls)}] {short_name}...", end=' ')
            
            deck = self.scrape_deck(url)
            if deck and deck['card_count'] >= 20:
                decks.append(deck)
                print(f"✓ {deck['card_count']} cards")
            else:
                print("✗")
        
        return decks
    
    def save_decks(self, decks: List[Dict], filename: str = "top_meta_decks.json"):
        """Save scraped decks."""
        output = self.data_dir / filename
        with open(output, 'w') as f:
            json.dump(decks, f, indent=2)
        print(f"\nSaved {len(decks)} decks to {output}")
        
        # Also save just the card lists for easy loading
        card_lists = {}
        for deck in decks:
            key = f"{deck['class']}_{deck['name'].replace(' ', '_')[:30]}"
            card_lists[key] = {
                'class': deck['class'],
                'name': deck['name'],
                'cards': deck['cards']
            }
        
        with open(self.data_dir / "meta_deck_lists.json", 'w') as f:
            json.dump(card_lists, f, indent=2)
        print(f"Saved card lists to {self.data_dir / 'meta_deck_lists.json'}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape top meta decks')
    parser.add_argument('--limit', type=int, default=30, help='Max decks to scrape')
    parser.add_argument('--data-dir', default='data', help='Data directory')
    
    args = parser.parse_args()
    
    scraper = MetaDeckScraper(args.data_dir)
    decks = scraper.scrape_top_decks(args.limit)
    
    if decks:
        scraper.save_decks(decks)
        
        # Summary by class
        print("\n" + "="*60)
        print("DECKS BY CLASS")
        print("="*60)
        
        by_class = {}
        for d in decks:
            cls = d['class']
            if cls not in by_class:
                by_class[cls] = []
            by_class[cls].append(d['name'])
        
        for cls in sorted(by_class.keys()):
            names = by_class[cls]
            print(f"\n{cls} ({len(names)}):")
            for name in names[:5]:
                print(f"  • {name[:50]}")
    else:
        print("No decks scraped")


if __name__ == '__main__':
    main()
