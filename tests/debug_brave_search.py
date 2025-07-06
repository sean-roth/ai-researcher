#!/usr/bin/env python3
"""Debug Brave Search API response structure."""

import asyncio
import json
import yaml
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from brave import AsyncBrave
except ImportError:
    print("Please install brave-search: pip install brave-search")
    sys.exit(1)

async def debug_brave_search():
    """Debug the Brave Search API response."""
    
    # Load config
    config_path = Path('config.yaml')
    if not config_path.exists():
        print("Error: config.yaml not found")
        print("Copy config.example.yaml to config.yaml and add your Brave API key")
        return
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    api_key = config.get('brave_search', {}).get('api_key')
    if not api_key or api_key == 'YOUR_ACTUAL_BRAVE_API_KEY_HERE':
        print("Error: Please add your Brave Search API key to config.yaml")
        return
    
    # Initialize Brave Search
    brave = AsyncBrave(api_key=api_key)
    
    # Test search
    query = "Japanese tech companies English training"
    print(f"Testing search for: '{query}'")
    print("-" * 60)
    
    try:
        # Perform search
        results = await brave.search(q=query, count=5)
        
        # Debug response structure
        print(f"Response type: {type(results)}")
        print(f"Response attributes: {dir(results)}")
        
        if isinstance(results, dict):
            print("\nResponse is a dictionary with keys:")
            for key in results.keys():
                print(f"  - {key}: {type(results[key])}")
            
            # Check for web results
            if 'web' in results:
                web_data = results['web']
                print(f"\nWeb data type: {type(web_data)}")
                if isinstance(web_data, dict) and 'results' in web_data:
                    print(f"Number of web results: {len(web_data['results'])}")
                    
                    # Show first result structure
                    if web_data['results']:
                        first_result = web_data['results'][0]
                        print("\nFirst result structure:")
                        print(json.dumps(first_result, indent=2))
        
        elif hasattr(results, 'web_results'):
            print(f"\nNumber of web_results: {len(results.web_results)}")
            if results.web_results:
                first = results.web_results[0]
                print(f"First result type: {type(first)}")
                print(f"First result attributes: {dir(first)}")
                if hasattr(first, '__dict__'):
                    print(f"First result data: {first.__dict__}")
        
        else:
            print("\nUnexpected response format!")
            print(f"Full response: {results}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_brave_search())
