#!/usr/bin/env python3
"""Complete diagnostic test to identify where the pipeline is failing."""

import asyncio
import logging
from pathlib import Path
import sys
import yaml
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def diagnose_pipeline():
    """Run complete diagnostics on the research pipeline."""
    
    print("\n" + "="*60)
    print("AI RESEARCHER DIAGNOSTIC TEST")
    print("="*60)
    
    results = {
        'config': False,
        'ollama': False,
        'brave_search': False,
        'crawling': False,
        'relevance': False,
        'extraction': False
    }
    
    # 1. Check configuration
    print("\n1. CHECKING CONFIGURATION...")
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("✅ Config file loaded")
        
        # Check Brave API key
        api_key = config.get('brave_search', {}).get('api_key', '')
        if api_key and api_key != 'YOUR_ACTUAL_BRAVE_API_KEY_HERE':
            print("✅ Brave API key configured")
            results['config'] = True
        else:
            print("❌ Brave API key not configured properly")
            
        # Check model
        model = config.get('ollama', {}).get('model', '')
        print(f"   Ollama model: {model}")
        
    except Exception as e:
        print(f"❌ Config error: {e}")
    
    # 2. Check Ollama
    print("\n2. CHECKING OLLAMA...")
    try:
        from ollama import AsyncClient
        client = AsyncClient()
        
        # Test with a simple prompt
        response = await client.generate(
            model=config['ollama']['model'],
            prompt="Respond with just the number 5"
        )
        
        if '5' in response['response']:
            print("✅ Ollama is working")
            results['ollama'] = True
        else:
            print(f"❌ Ollama gave unexpected response: {response['response']}")
            
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        print("   Make sure Ollama is running: ollama serve")
    
    # 3. Check Brave Search (if configured)
    print("\n3. CHECKING BRAVE SEARCH...")
    if results['config']:
        try:
            from brave import AsyncBrave
            brave = AsyncBrave(api_key=api_key)
            
            # Simple search
            search_results = await brave.search(q="test", count=1)
            
            # Check response type
            if isinstance(search_results, dict):
                if 'web' in search_results and 'results' in search_results['web']:
                    print("✅ Brave Search returns dictionary format")
                    print(f"   Found {len(search_results['web']['results'])} results")
                    results['brave_search'] = True
                else:
                    print(f"❌ Unexpected dictionary structure: {search_results.keys()}")
            else:
                print(f"❌ Unexpected response type: {type(search_results)}")
                
        except Exception as e:
            print(f"❌ Brave Search error: {e}")
    else:
        print("⚠️  Skipping - API key not configured")
    
    # 4. Check Crawl4ai
    print("\n4. CHECKING CRAWL4AI...")
    try:
        from crawl4ai import AsyncWebCrawler
        
        async with AsyncWebCrawler(verbose=False) as crawler:
            # Test with a simple page
            result = await crawler.arun(url="https://example.com")
            
            if result.success and result.markdown:
                print(f"✅ Crawl4ai working - crawled {len(result.markdown)} chars")
                results['crawling'] = True
            else:
                print("❌ Crawl4ai failed to crawl example.com")
                
    except Exception as e:
        print(f"❌ Crawl4ai error: {e}")
    
    # 5. Test complete pipeline with a known good content
    print("\n5. TESTING COMPLETE PIPELINE...")
    if results['ollama'] and results['crawling']:
        try:
            from src.web_researcher import WebResearcher
            researcher = WebResearcher('config.yaml')
            
            # Test content that should definitely be relevant
            test_content = """
            Rakuten, the Japanese e-commerce giant, has made English its official corporate language.
            The company faces challenges with engineers struggling to communicate in English during meetings.
            They have implemented Berlitz training programs and require TOEIC scores of 700.
            Hiroshi Mikitani, the CEO, believes English proficiency is crucial for global expansion.
            """
            
            # Test relevance
            relevance = await researcher.quick_relevance_check(
                test_content,
                "Japanese tech companies English training",
                "Rakuten English Policy"
            )
            print(f"   Relevance score: {relevance}/10")
            
            if relevance >= 5:
                results['relevance'] = True
                
                # Test extraction
                extracted = await researcher.extract_structured_data(
                    test_content,
                    "Japanese tech companies English training",
                    "test://example"
                )
                
                if extracted.get('companies') or extracted.get('english_challenges'):
                    print("✅ Extraction working")
                    print(f"   Found: {len(extracted.get('companies', []))} companies")
                    print(f"   Found: {len(extracted.get('english_challenges', []))} challenges")
                    results['extraction'] = True
                else:
                    print("❌ Extraction failed - no data extracted")
                    print(f"   Raw response: {json.dumps(extracted, indent=2)}")
            else:
                print(f"❌ Relevance check too strict (score: {relevance})")
                
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    
    working = sum(results.values())
    total = len(results)
    
    for component, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {component.replace('_', ' ').title()}: {'Working' if status else 'Failed'}")
    
    print(f"\nOverall: {working}/{total} components working")
    
    if working < total:
        print("\nRECOMMENDATIONS:")
        if not results['config']:
            print("- Add your Brave Search API key to config.yaml")
        if not results['ollama']:
            print("- Make sure Ollama is running: ollama serve")
            print("- Check that the model is installed: ollama pull dolphin3:latest")
        if not results['brave_search'] and results['config']:
            print("- Check your Brave Search API key is valid")
            print("- The API might have changed - check the response format")
        if not results['relevance']:
            print("- Relevance scoring is too strict - may need to adjust prompts")
        if not results['extraction']:
            print("- Extraction prompts may need adjustment for your model")

if __name__ == "__main__":
    asyncio.run(diagnose_pipeline())
