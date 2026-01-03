import urllib.request
import json
import xml.etree.ElementTree as ET
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.replay_parser import HSReplayParser, extract_training_pairs

REPLAY_ID = "u3FYcWm2vXr9ZNtZsyavC6"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

import gzip
import io

# ... imports ...

def download_replay():
    print(f"Fetching metadata for {REPLAY_ID}...")
    req = urllib.request.Request(f'https://hsreplay.net/api/v1/games/{REPLAY_ID}/', headers=HEADERS)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            xml_url = data.get('replay_xml')
            if not xml_url:
                print("Error: No replay_xml URL found in metadata")
                sys.exit(1)
            
            print(f"Downloading XML from S3...")
            with urllib.request.urlopen(xml_url) as xml_response:
                content = xml_response.read()
                
                # Check for gzip magic number (1f 8b)
                if content.startswith(b'\x1f\x8b'):
                    print("Detected GZIP content, decompressing...")
                    with gzip.GzipFile(fileobj=io.BytesIO(content)) as gz:
                        return gz.read()
                return content
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)

def main():
    # 1. Download
    xml_content = download_replay()
    
    # 2. Save to temp file (parser expects file path)
    parse_file = "temp_replay.xml"
    with open(parse_file, "wb") as f:
        f.write(xml_content)
    
    print(f"Saved {len(xml_content)} bytes to {parse_file}")
    
    # 3. Parse
    print("Parsing replay...")
    parser = HSReplayParser()
    replay = parser.parse_file(parse_file)
    
    if not replay:
        print("Parsing failed!")
        sys.exit(1)
        
    print(f"Parse successful!")
    print(f"Game ID: {replay.game_id}")
    print(f"Matchup: {replay.player1_class} vs {replay.player2_class}")
    print(f"Winner: Player {replay.winner}")
    print(f"Turns: {len(replay.turns)}")
    
    total_actions = sum(len(t.actions) for t in replay.turns)
    print(f"Total Actions: {total_actions}")
    
    # 4. Extract Pairs
    print("\nExtracting training pairs...")
    try:
        # Wrap in list as function expects list
        pairs = extract_training_pairs([replay])
        print(f"Extracted {len(pairs)} training pairs")
        
        if pairs:
            print("\nSample Pair 0:")
            print(json.dumps(pairs[0]['action_label'], indent=2)) # Just print label or keys
            print("Keys:", pairs[0].keys())
    except Exception as e:
        print(f"Extraction failed: {e}")
    
    # Cleanup
    # if os.path.exists(parse_file):
    #    os.remove(parse_file)
    
    # Inspect first 500 chars
    with open(parse_file, 'r', encoding='utf-8') as f:
        print("\nXML Head:\n", f.read(1000))

if __name__ == "__main__":
    main()
