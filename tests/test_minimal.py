"""Minimal test to verify all components are working."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ollama import AsyncClient
from crawl4ai import AsyncWebCrawler


async def test_research_pipeline():
    """Test the basic research pipeline components."""
    print("🔍 Testing AI Researcher Components...\n")
    
    # 1. Test Ollama connection
    print("1. Testing Ollama connection...")
    try:
        ollama = AsyncClient()
        test_prompt = "What makes a good research question? Answer in one sentence."
        response = await ollama.generate(
            model='dolphin-llama3:8b',
            prompt=test_prompt
        )
        print(f"✓ Ollama working: {response['response'].strip()}")
    except Exception as e:
        print(f"✗ Ollama error: {e}")
        print("  Make sure Ollama is running and dolphin-llama3:8b is installed")
        return
    
    # 2. Test web search with Crawl4ai
    print("\n2. Testing web search...")
    crawler = None
    try:
        crawler = AsyncWebCrawler()
        await crawler.start()
        
        # Simple search
        results = await crawler.search("Rakuten English training needs", max_results=3)
        print(f"✓ Found {len(results)} search results")
        
        if results:
            print(f"  First result: {results[0].get('title', 'No title')[:60]}...")
            
    except Exception as e:
        print(f"✗ Web search error: {e}")
        return
    finally:
        if crawler:
            await crawler.close()
    
    # 3. Test simple research cycle
    print("\n3. Testing research analysis...")
    try:
        research_prompt = f"""
        Based on these search results about Rakuten:
        {[r.get('snippet', '')[:100] for r in results[:2]]}
        
        What English training challenges might they face?
        Answer in 2-3 bullet points.
        """
        
        analysis = await ollama.generate(
            model='dolphin-llama3:8b',
            prompt=research_prompt
        )
        print("✓ Analysis generated:")
        print(f"  {analysis['response'].strip()}")
        
    except Exception as e:
        print(f"✗ Analysis error: {e}")
        return
    
    # 4. Test report generation
    print("\n4. Testing report generation...")
    try:
        report = f"""
# Rakuten English Training Analysis

## Test Report
Generated: {asyncio.get_event_loop().time()}

## Key Findings
{analysis['response']}

## Sources
- {results[0].get('url', 'No URL')}
- {results[1].get('url', 'No URL') if len(results) > 1 else 'No second source'}

---
*This is a test report from the minimal test suite*
        """
        
        # Save test report
        test_report_path = Path('test_report.md')
        test_report_path.write_text(report)
        print(f"✓ Report generated and saved to {test_report_path}")
        
    except Exception as e:
        print(f"✗ Report generation error: {e}")
        return
    
    print("\n✅ All components working! Ready to build the full researcher.")


if __name__ == "__main__":
    print("AI Researcher - Minimal Test Suite")
    print("=" * 40)
    asyncio.run(test_research_pipeline())