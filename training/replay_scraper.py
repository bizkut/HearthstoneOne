"""
HSReplay Scraper for Meta-Aware Training

Discovers and downloads game replays from HSReplay.net for training.
Uses the public archetypes API and browser automation to find replay links.
"""

import os
import sys
import json
import gzip
import time
import sqlite3
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import io

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# User-Agent to mimic browser
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

@dataclass
class Replay:
    """Represents a discovered replay."""
    shortid: str
    archetype_id: Optional[int] = None
    player_class: Optional[str] = None
    downloaded: bool = False
    download_path: Optional[str] = None


class ReplayDatabase:
    """SQLite database to track discovered and downloaded replays."""
    
    def __init__(self, db_path: str = 'data/replays.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_schema()
    
    def _init_schema(self):
        """Create tables if they don't exist."""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS replays (
                shortid TEXT PRIMARY KEY,
                archetype_id INTEGER,
                player_class TEXT,
                downloaded INTEGER DEFAULT 0,
                download_path TEXT,
                discovered_at TEXT,
                downloaded_at TEXT
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS archetypes (
                id INTEGER PRIMARY KEY,
                name TEXT,
                player_class TEXT,
                last_crawled TEXT
            )
        ''')
        self.conn.commit()
    
    def add_replay(self, replay: Replay) -> bool:
        """Add a replay if not already in database. Returns True if new."""
        try:
            self.conn.execute(
                'INSERT INTO replays (shortid, archetype_id, player_class, discovered_at) VALUES (?, ?, ?, ?)',
                (replay.shortid, replay.archetype_id, replay.player_class, datetime.now().isoformat())
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Already exists
    
    def mark_downloaded(self, shortid: str, path: str):
        """Mark a replay as downloaded."""
        self.conn.execute(
            'UPDATE replays SET downloaded = 1, download_path = ?, downloaded_at = ? WHERE shortid = ?',
            (path, datetime.now().isoformat(), shortid)
        )
        self.conn.commit()
    
    def get_pending_replays(self, limit: int = 100) -> List[str]:
        """Get replay IDs that haven't been downloaded yet."""
        cursor = self.conn.execute(
            'SELECT shortid FROM replays WHERE downloaded = 0 LIMIT ?',
            (limit,)
        )
        return [row[0] for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        cursor = self.conn.execute('SELECT COUNT(*) FROM replays')
        total = cursor.fetchone()[0]
        cursor = self.conn.execute('SELECT COUNT(*) FROM replays WHERE downloaded = 1')
        downloaded = cursor.fetchone()[0]
        return {'total': total, 'downloaded': downloaded, 'pending': total - downloaded}
    
    def close(self):
        self.conn.close()


class HSReplayScraper:
    """Main scraper class for HSReplay.net."""
    
    def __init__(self, 
                 output_dir: str = 'data/replays',
                 db_path: str = 'data/replays.db',
                 rate_limit: float = 1.0):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db = ReplayDatabase(db_path)
        self.rate_limit = rate_limit  # seconds between requests
        self.last_request_time = 0
    
    def _request(self, url: str) -> Optional[bytes]:
        """Make a rate-limited HTTP request."""
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        
        headers = {'User-Agent': USER_AGENT}
        req = urllib.request.Request(url, headers=headers)
        
        try:
            self.last_request_time = time.time()
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            print(f"  HTTP Error {e.code}: {url}")
            return None
        except Exception as e:
            print(f"  Request failed: {e}")
            return None
    
    def fetch_archetypes(self) -> List[Dict]:
        """Fetch all archetypes from the API."""
        print("[Scraper] Fetching archetypes...")
        data = self._request('https://hsreplay.net/api/v1/archetypes/')
        if data:
            archetypes = json.loads(data.decode('utf-8'))
            print(f"  Found {len(archetypes)} archetypes")
            return archetypes
        return []
    
    def discover_replays_from_recent_games(self, page_url: str) -> List[str]:
        """
        Discover replay IDs from an archetype page.
        
        Note: This requires browser automation since the replay list
        is loaded via JavaScript. For now, we'll use a known sample
        or implement Selenium/Playwright later.
        """
        # TODO: Implement browser automation to scrape replay links
        # For now, return empty - we'll use the direct game API approach
        return []
    
    def discover_replays_from_sample_list(self, sample_ids: List[str]) -> int:
        """Add known sample IDs to the database."""
        count = 0
        for sid in sample_ids:
            replay = Replay(shortid=sid)
            if self.db.add_replay(replay):
                count += 1
        print(f"[Scraper] Added {count} new replay IDs from sample list")
        return count
    
    def download_replay(self, shortid: str) -> bool:
        """Download a single replay by its shortid."""
        # Get metadata
        metadata_url = f'https://hsreplay.net/api/v1/games/{shortid}/'
        data = self._request(metadata_url)
        if not data:
            return False
        
        try:
            metadata = json.loads(data.decode('utf-8'))
            xml_url = metadata.get('replay_xml')
            if not xml_url:
                print(f"  No XML URL for {shortid}")
                return False
            
            # Download XML (possibly gzipped)
            xml_data = self._request(xml_url)
            if not xml_data:
                return False
            
            # Decompress if gzipped
            if xml_data.startswith(b'\x1f\x8b'):
                with gzip.GzipFile(fileobj=io.BytesIO(xml_data)) as gz:
                    xml_data = gz.read()
            
            # Save to file
            output_path = self.output_dir / f'{shortid}.xml'
            with open(output_path, 'wb') as f:
                f.write(xml_data)
            
            self.db.mark_downloaded(shortid, str(output_path))
            return True
            
        except Exception as e:
            print(f"  Error downloading {shortid}: {e}")
            return False
    
    def run(self, max_replays: int = 100, sample_ids: Optional[List[str]] = None):
        """
        Run the scraper.
        
        Args:
            max_replays: Maximum number of replays to download
            sample_ids: Optional list of known replay IDs to start with
        """
        print(f"\n{'='*60}")
        print(f"[Scraper] HSReplay Scraper Starting")
        print(f"  Output: {self.output_dir}")
        print(f"  Rate Limit: {self.rate_limit}s between requests")
        print(f"{'='*60}\n")
        
        # Step 1: Fetch archetypes (for metadata, not discovery yet)
        archetypes = self.fetch_archetypes()
        
        # Step 2: Add sample IDs if provided
        if sample_ids:
            self.discover_replays_from_sample_list(sample_ids)
        
        # Step 3: Download pending replays
        stats = self.db.get_stats()
        print(f"\n[Scraper] Database: {stats['total']} total, {stats['downloaded']} downloaded, {stats['pending']} pending")
        
        pending = self.db.get_pending_replays(limit=max_replays)
        if not pending:
            print("[Scraper] No pending replays to download")
            return
        
        print(f"\n[Scraper] Downloading {len(pending)} replays...")
        success = 0
        for i, shortid in enumerate(pending):
            print(f"  [{i+1}/{len(pending)}] {shortid}...", end=' ')
            if self.download_replay(shortid):
                print("OK")
                success += 1
            else:
                print("FAILED")
        
        print(f"\n[Scraper] Complete! Downloaded {success}/{len(pending)} replays")
        
        # Final stats
        stats = self.db.get_stats()
        print(f"[Scraper] Final: {stats['total']} total, {stats['downloaded']} downloaded")
    
    def close(self):
        self.db.close()


def main():
    parser = argparse.ArgumentParser(description='HSReplay Scraper for Meta-Aware Training')
    parser.add_argument('--output', default='data/replays', help='Output directory for XML files')
    parser.add_argument('--db', default='data/replays.db', help='SQLite database path')
    parser.add_argument('--max-replays', type=int, default=100, help='Maximum replays to download')
    parser.add_argument('--rate-limit', type=float, default=1.0, help='Seconds between requests')
    parser.add_argument('--sample-ids', nargs='*', help='Sample replay IDs to start with')
    
    args = parser.parse_args()
    
    # Default sample IDs for testing
    default_samples = [
        'u3FYcWm2vXr9ZNtZsyavC6',  # Known working replay
    ]
    
    sample_ids = args.sample_ids if args.sample_ids else default_samples
    
    scraper = HSReplayScraper(
        output_dir=args.output,
        db_path=args.db,
        rate_limit=args.rate_limit
    )
    
    try:
        scraper.run(max_replays=args.max_replays, sample_ids=sample_ids)
    finally:
        scraper.close()


if __name__ == '__main__':
    main()
