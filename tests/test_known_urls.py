#!/usr/bin/env python3
"""Test extraction with known good URLs about Japanese tech companies."""

import asyncio
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.web_researcher import WebResearcher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Known good URLs about Japanese tech companies and English
GOOD_URLS = [
    {
        'url': 'https://www.japantimes.co.jp/business/2023/06/19/english-proficiency-japan/',
        'title': 'Japan Times - English Proficiency in Japanese Companies',
        'description': 'Article about English challenges in Japanese businesses'
    },
    {
        'url': 'https://biz-journal.jp/2023/03/post_335893.html',
        'title': 'Japanese Tech Companies and English Communication',
        'description': 'Business journal article on language barriers'
    },
    {
        'url': 'https://www.humanresourcesonline.net/5-things-to-know-about-japans-workplace-english-needs',
        'title': 'Japan Workplace English Needs - HR Online',
        'description': 'HR perspective on English training in Japan'
    },
    {
        'url': 'https://toyokeizai.net/articles/-/669789',
        'title': 'Toyo Keizai - Japanese Companies English Training Investment',
        'description': 'Economic analysis of corporate English training'
    }
]

async def test_with_good_urls():
    """Test extraction with URLs we know should have good content."""
    
    print("Testing extraction with known good URLs...")
    print("=" * 60)
    
    # Create a mock web researcher
    researcher = WebResearcher('config.yaml')
    
    # Manually test each URL
    from crawl4ai import AsyncWebCrawler
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        for url_info in GOOD_URLS:
            print(f"\n{'='*60}")
            print(f"Testing: {url_info['title']}")
            print(f"URL: {url_info['url']}")
            print("-" * 60)
            
            try:
                # Crawl the page
                result = await crawler.arun(
                    url=url_info['url'],
                    word_count_threshold=100,
                    remove_overlay_elements=True
                )
                
                if result.success and result.markdown:
                    content_length = len(result.markdown)
                    print(f"✓ Crawled {content_length} characters")
                    
                    # Test relevance check
                    relevance = await researcher.quick_relevance_check(
                        result.markdown[:3000],
                        "Japanese tech companies English training challenges",
                        url_info['title']
                    )
                    print(f"✓ Relevance score: {relevance}/10")
                    
                    # Extract structured data
                    if relevance >= 5:
                        extracted = await researcher.extract_structured_data(
                            result.markdown[:15000],
                            "Japanese tech companies English training challenges",
                            url_info['url']
                        )
                        
                        print("\nExtracted Data:")
                        if extracted.get('companies'):
                            print(f"  Companies: {extracted['companies'][:3]}")
                        if extracted.get('english_challenges'):
                            print(f"  Challenges: {extracted['english_challenges'][:2]}")
                        if extracted.get('current_solutions'):
                            print(f"  Solutions: {extracted['current_solutions'][:2]}")
                        if extracted.get('key_insights'):
                            print(f"  Insights: {extracted['key_insights'][:1]}")
                        
                        if not extracted.get('relevant_findings'):
                            print("  ⚠️  No relevant findings extracted")
                    else:
                        print("  ⚠️  Content not relevant enough to extract")
                        
                else:
                    print(f"✗ Failed to crawl: {result.error if hasattr(result, 'error') else 'Unknown error'}")
                    
            except Exception as e:
                print(f"✗ Error: {e}")
                import traceback
                traceback.print_exc()

async def test_search_functionality():
    """Test the full search and analyze functionality."""
    print("\n" + "="*60)
    print("Testing full search functionality...")
    print("="*60)
    
    researcher = WebResearcher('config.yaml')
    
    queries = [
        "Rakuten English training program corporate",
        "Japanese tech companies struggling English communication 2024",
        "LinkedIn HR director Japanese technology company English"
    ]
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        findings = await researcher.search_and_analyze(
            query,
            ['news', 'corporate sites', 'industry reports']
        )
        
        print(f"Found {len(findings)} relevant sources")
        for finding in findings:
            print(f"  - {finding['title']} (score: {finding['quality_score']})")

async def main():
    """Run all tests."""
    # First test with known URLs
    await test_with_good_urls()
    
    # Then test search functionality
    await test_search_functionality()

if __name__ == "__main__":
    asyncio.run(main())
