#!/usr/bin/env python3
"""Simple test to debug why content isn't being marked as relevant."""

import asyncio
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.web_researcher import WebResearcher
from crawl4ai import AsyncWebCrawler

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_single_url():
    """Test a single URL with detailed debugging."""
    
    # A URL we know should have relevant content
    test_url = {
        'url': 'https://www.tokyodev.com/companies/',
        'title': 'Tech Companies in Tokyo',
        'description': 'List of tech companies in Tokyo'
    }
    
    print(f"\nTesting URL: {test_url['url']}")
    print("=" * 60)
    
    researcher = WebResearcher('config.yaml')
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        # Step 1: Crawl
        print("\n1. CRAWLING...")
        result = await crawler.arun(
            url=test_url['url'],
            word_count_threshold=50,  # Lower threshold
            remove_overlay_elements=True
        )
        
        if not result.success:
            print(f"❌ Crawl failed: {result.error if hasattr(result, 'error') else 'Unknown error'}")
            return
            
        print(f"✅ Crawled successfully: {len(result.markdown)} characters")
        print(f"   First 500 chars: {result.markdown[:500]}...")
        
        # Step 2: Check relevance
        print("\n2. CHECKING RELEVANCE...")
        relevance = await researcher.quick_relevance_check(
            result.markdown[:3000],
            "Japanese tech companies",
            test_url['title']
        )
        print(f"✅ Relevance score: {relevance}/10")
        
        # Step 3: Extract data (regardless of score for testing)
        print("\n3. EXTRACTING DATA (forcing extraction regardless of score)...")
        extracted = await researcher.extract_structured_data(
            result.markdown[:10000],
            "Japanese tech companies English training",
            test_url['url']
        )
        
        print("\n4. EXTRACTED DATA:")
        print(f"   Relevant findings: {extracted.get('relevant_findings', False)}")
        print(f"   Companies found: {len(extracted.get('companies', []))}")
        if extracted.get('companies'):
            print(f"   - First few: {extracted['companies'][:3]}")
        print(f"   Challenges found: {len(extracted.get('english_challenges', []))}")
        print(f"   Solutions found: {len(extracted.get('current_solutions', []))}")
        print(f"   Decision makers: {len(extracted.get('decision_makers', []))}")
        print(f"   Key insights: {len(extracted.get('key_insights', []))}")
        
        # Show raw extraction response for debugging
        print("\n5. RAW EXTRACTED DATA:")
        import json
        print(json.dumps(extracted, indent=2))

async def test_relevance_scoring():
    """Test relevance scoring with different content."""
    
    researcher = WebResearcher('config.yaml')
    
    test_contents = [
        {
            'title': 'Japanese Tech Companies',
            'content': 'This article discusses various Japanese technology companies including Rakuten, Mercari, and LINE. These companies have been expanding globally and face English communication challenges.'
        },
        {
            'title': 'Random Article',
            'content': 'This is about cooking recipes and has nothing to do with technology or business.'
        },
        {
            'title': 'Jobs in Japan',
            'content': 'Software developer positions available at Japanese tech companies. English required. Companies like Rakuten and Mercari are hiring.'
        }
    ]
    
    print("\n\nTESTING RELEVANCE SCORING")
    print("=" * 60)
    
    for test in test_contents:
        print(f"\nTitle: {test['title']}")
        score = await researcher.quick_relevance_check(
            test['content'],
            "Japanese tech companies English",
            test['title']
        )
        print(f"Score: {score}/10")

async def main():
    """Run all tests."""
    await test_single_url()
    await test_relevance_scoring()

if __name__ == "__main__":
    asyncio.run(main())
