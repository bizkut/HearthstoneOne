#!/usr/bin/env python3
"""
HSReplay Deck Scraper

Attempts to scrape top deck lists from hsreplay.net using urllib.
"""

import urllib.request
import urllib.error
import json
import re
import sys
import os
from typing import List, Dict, Optional

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fetch_page(url: str) -> Optional[str]:
    """Fetch page content with browser-like headers."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            # Handle gzip
            if response.info().get('Content-Encoding') == 'gzip':
                import gzip
                return gzip.decompress(response.read()).decode('utf-8')
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def try_api_endpoints():
    """Try various HSReplay API endpoints."""
    
    endpoints = [
        # Public API endpoints
        ("Archetypes", "https://hsreplay.net/api/v1/archetypes/"),
        ("Deck Summary", "https://hsreplay.net/analytics/query/list_decks_by_win_rate/"),
        ("Meta Overview", "https://hsreplay.net/api/v1/meta/"),
    ]
    
    results = {}
    
    for name, url in endpoints:
        print(f"\n[{name}] Trying: {url}")
        content = fetch_page(url)
        
        if content:
            # Try to parse as JSON
            try:
                data = json.loads(content)
                print(f"  ✓ Success! Got JSON with {len(data) if isinstance(data, list) else 'dict'} items")
                results[name] = data
                
                # Show sample
                if isinstance(data, list) and len(data) > 0:
                    print(f"  Sample: {json.dumps(data[0], indent=2)[:500]}...")
                elif isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    print(f"  Keys: {keys}")
            except json.JSONDecodeError:
                print(f"  Got HTML response ({len(content)} chars)")
                # Try to find embedded JSON in HTML
                json_match = re.search(r'window\.__REDUX_STATE__\s*=\s*({.*?});', content, re.DOTALL)
                if json_match:
                    print(f"  Found embedded Redux state!")
                    try:
                        redux_data = json.loads(json_match.group(1))
                        results[name] = redux_data
                        print(f"  Redux keys: {list(redux_data.keys())[:5]}")
                    except:
                        pass
        else:
            print(f"  ✗ Failed")
    
    return results


def scrape_decks_page():
    """Try to scrape the main decks page."""
    print("\n" + "="*60)
    print("Attempting to scrape https://hsreplay.net/decks/")
    print("="*60)
    
    url = "https://hsreplay.net/decks/"
    content = fetch_page(url)
    
    if not content:
        print("Failed to fetch decks page")
        return None
    
    print(f"Got response: {len(content)} characters")
    
    # Look for deck data patterns
    patterns = [
        (r'\"deckId\":\"([^\"]+)\"', "Deck IDs"),
        (r'\"archetype\":\"([^\"]+)\"', "Archetypes"),
        (r'\"playerClass\":\"([^\"]+)\"', "Classes"),
        (r'data-deck-id=\"([^\"]+)\"', "Data attributes"),
        (r'/decks/([A-Za-z0-9]+)/', "Deck URLs"),
    ]
    
    for pattern, name in patterns:
        matches = re.findall(pattern, content)
        if matches:
            unique = list(set(matches))[:10]
            print(f"  Found {len(matches)} {name}: {unique[:5]}...")
    
    # Check for Cloudflare block
    if 'Just a moment' in content or 'cf-browser-verification' in content:
        print("\n⚠️  Cloudflare challenge detected - page is protected")
        return None
    
    # Try to find Next.js data
    next_data = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', content, re.DOTALL)
    if next_data:
        print("\nFound Next.js data!")
        try:
            data = json.loads(next_data.group(1))
            print(f"  Props keys: {list(data.get('props', {}).keys())}")
            return data
        except:
            pass
    
    return content


def try_hearthstone_top_decks_api():
    """Try alternative: hearthstone-decks.net or similar."""
    print("\n" + "="*60)
    print("Trying alternative: d0nkey.top API")
    print("="*60)
    
    # d0nkey.top has a public API
    url = "https://www.d0nkey.top/api/decks"
    content = fetch_page(url)
    
    if content:
        try:
            data = json.loads(content)
            print(f"✓ Got {len(data)} decks from d0nkey.top!")
            if data:
                print(f"Sample deck: {json.dumps(data[0], indent=2)[:1000]}")
            return data
        except:
            print("Failed to parse response")
    
    return None


def main():
    print("HSReplay Deck Scraper")
    print("=" * 60)
    
    # Try API endpoints first
    api_results = try_api_endpoints()
    
    # Try main page
    page_data = scrape_decks_page()
    
    # Try alternative source
    alt_data = try_hearthstone_top_decks_api()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if api_results.get('Archetypes'):
        archetypes = api_results['Archetypes']
        print(f"\n✓ Got {len(archetypes)} archetypes from API")
        
        # Save archetypes
        with open('data/archetypes.json', 'w') as f:
            json.dump(archetypes, f, indent=2)
        print("  Saved to data/archetypes.json")
        
        # Print top archetypes by class
        by_class = {}
        for arch in archetypes:
            cls = arch.get('player_class_name', 'Unknown')
            if cls not in by_class:
                by_class[cls] = []
            by_class[cls].append(arch.get('name', 'Unknown'))
        
        print("\n  Archetypes by class:")
        for cls, names in sorted(by_class.items()):
            print(f"    {cls}: {', '.join(names[:3])}...")
    
    if alt_data:
        print(f"\n✓ Got {len(alt_data)} decks from d0nkey.top")
        with open('data/alt_decks.json', 'w') as f:
            json.dump(alt_data, f, indent=2)
        print("  Saved to data/alt_decks.json")


if __name__ == '__main__':
    main()
