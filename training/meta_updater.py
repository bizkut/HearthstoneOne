"""
Meta Update Pipeline

Downloads latest HSReplay data and fine-tunes the model on current meta.
Designed to run weekly to keep the AI competitive.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class HSReplayFetcher:
    """
    Fetches replay data from HSReplay.net API.
    
    Note: Requires HSReplay API key for production use.
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: str = 'data/meta_cache'):
        self.api_key = api_key or os.environ.get('HSREPLAY_API_KEY')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_top_decks(self, 
                        rank_range: str = 'LEGEND',
                        time_range: str = 'LAST_7_DAYS',
                        limit: int = 20) -> List[Dict]:
        """
        Fetch top performing decks from HSReplay.
        
        Args:
            rank_range: LEGEND, DIAMOND, PLATINUM, etc.
            time_range: LAST_1_DAY, LAST_3_DAYS, LAST_7_DAYS, LAST_14_DAYS
            limit: Maximum decks to fetch
        
        Returns:
            List of deck dictionaries with archetype and card list
        """
        # Placeholder: In production, this would call HSReplay API
        # https://hsreplay.net/api/v1/archetypes/
        
        print(f"[MetaUpdater] Would fetch top {limit} {rank_range} decks from last {time_range}")
        print("[MetaUpdater] Note: HSReplay API integration requires API key")
        
        # Return mock data for testing
        return self._get_mock_decks(limit)
    
    def _get_mock_decks(self, limit: int) -> List[Dict]:
        """Return mock deck data for testing."""
        archetypes = [
            {'name': 'Aggro Paladin', 'archetype': 'AGGRO', 'class': 'PALADIN'},
            {'name': 'Control Warrior', 'archetype': 'CONTROL', 'class': 'WARRIOR'},
            {'name': 'Miracle Rogue', 'archetype': 'COMBO', 'class': 'ROGUE'},
            {'name': 'Midrange Hunter', 'archetype': 'MIDRANGE', 'class': 'HUNTER'},
            {'name': 'Freeze Mage', 'archetype': 'OTK', 'class': 'MAGE'},
        ]
        
        return archetypes[:limit]
    
    def fetch_replays_for_archetype(self,
                                     archetype_id: str,
                                     rank_range: str = 'LEGEND',
                                     limit: int = 100) -> List[str]:
        """
        Fetch replay URLs for a specific archetype.
        
        Args:
            archetype_id: HSReplay archetype ID
            rank_range: LEGEND, DIAMOND, etc.
            limit: Maximum replays to fetch
        
        Returns:
            List of replay download URLs
        """
        print(f"[MetaUpdater] Would fetch {limit} replays for archetype {archetype_id}")
        return []


class MetaUpdater:
    """
    Orchestrates meta update process.
    
    1. Fetches current top decks
    2. Downloads recent replays
    3. Parses replays to training data
    4. Fine-tunes model on new data
    """
    
    def __init__(self,
                 data_dir: str = 'data',
                 models_dir: str = 'models',
                 api_key: Optional[str] = None):
        self.data_dir = Path(data_dir)
        self.models_dir = Path(models_dir)
        self.fetcher = HSReplayFetcher(api_key)
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def run_update(self,
                   epochs: int = 10,
                   learning_rate: float = 1e-5,
                   save_backup: bool = True) -> bool:
        """
        Run full meta update pipeline.
        
        Args:
            epochs: Training epochs for fine-tuning
            learning_rate: Lower LR for fine-tuning to avoid catastrophic forgetting
            save_backup: Whether to backup current model before updating
        
        Returns:
            True if update was successful
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        print(f"\n{'='*60}")
        print(f"[MetaUpdater] Starting meta update at {timestamp}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Fetch current meta
            print("[Step 1/4] Fetching current meta decks...")
            top_decks = self.fetcher.fetch_top_decks(limit=10)
            print(f"  Found {len(top_decks)} top archetypes")
            
            # Step 2: Fetch replays
            print("\n[Step 2/4] Fetching recent replays...")
            replay_urls = []
            for deck in top_decks[:5]:  # Top 5 archetypes
                urls = self.fetcher.fetch_replays_for_archetype(
                    deck.get('archetype', 'UNKNOWN'),
                    limit=50
                )
                replay_urls.extend(urls)
            print(f"  Collected {len(replay_urls)} replay URLs")
            
            # Step 3: Parse replays
            print("\n[Step 3/4] Parsing replays...")
            training_data_path = self.data_dir / f'meta_update_{timestamp}.json'
            print(f"  Would save to: {training_data_path}")
            
            # Step 4: Fine-tune model
            print("\n[Step 4/4] Fine-tuning model...")
            print(f"  Epochs: {epochs}")
            print(f"  Learning rate: {learning_rate}")
            
            # Backup current model
            if save_backup:
                backup_path = self.models_dir / f'backup_{timestamp}'
                print(f"  Backup would be saved to: {backup_path}")
            
            print("\n[MetaUpdater] Update complete (dry run - no API key)")
            return True
            
        except Exception as e:
            print(f"\n[MetaUpdater] Update failed: {e}")
            return False
    
    def get_last_update_time(self) -> Optional[datetime]:
        """Get timestamp of last meta update."""
        update_log = self.data_dir / 'meta_update_log.json'
        if update_log.exists():
            with open(update_log) as f:
                log = json.load(f)
                return datetime.fromisoformat(log.get('last_update', ''))
        return None
    
    def should_update(self, days: int = 7) -> bool:
        """Check if update is needed based on time since last update."""
        last_update = self.get_last_update_time()
        if last_update is None:
            return True
        return datetime.now() - last_update > timedelta(days=days)


def main():
    parser = argparse.ArgumentParser(description='HearthstoneOne Meta Update Pipeline')
    parser.add_argument('--data-dir', default='data', help='Data directory')
    parser.add_argument('--models-dir', default='models', help='Models directory')
    parser.add_argument('--epochs', type=int, default=10, help='Fine-tuning epochs')
    parser.add_argument('--lr', type=float, default=1e-5, help='Learning rate')
    parser.add_argument('--force', action='store_true', help='Force update even if recent')
    parser.add_argument('--dry-run', action='store_true', help='Dry run without actual changes')
    
    args = parser.parse_args()
    
    updater = MetaUpdater(
        data_dir=args.data_dir,
        models_dir=args.models_dir
    )
    
    # Check if update needed
    if not args.force and not updater.should_update():
        print("[MetaUpdater] Last update was recent, skipping (use --force to override)")
        return
    
    # Run update
    success = updater.run_update(
        epochs=args.epochs,
        learning_rate=args.lr
    )
    
    if success:
        print("\n✅ Meta update completed successfully")
    else:
        print("\n❌ Meta update failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
