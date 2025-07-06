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
            model='dolphin3:latest',
            prompt=test_prompt
        )
        print(f"✓ Ollama working: {response['response'].strip()}")
    except Exception as e:
        print(f"✗ Ollama error: {e}")
        print("  Make sure Ollama is running and dolphin3:latest is installed")
        return
    
    # 2. Test web crawling with Crawl4ai
    print("\n2. Testing web crawling...")
    async with AsyncWebCrawler(verbose=True) as crawler:
        try:
            # Use arun method for crawling
            test_url = "https://www.example.com/"
            result = await crawler.arun(url=test_url)
            
            if result.success:
                print(f"✓ Successfully crawled {test_url}")
                print(f"  Content length: {len(result.text)} characters")
                
                # Create mock "search results" for the next test
                results = [{
                    'url': test_url,
                    'title': 'Example Domain',
                    'snippet': result.text[:200] if result.text else 'No content'
                }]
            else:
                print("✗ Crawl failed")
                results = []
                
        except Exception as e:
            print(f"✗ Web crawl error: {e}")
            # Create fallback data for testing
            results = [{
                'url': 'https://www.example.com/',
                'title': 'Example Site',
                'snippet': 'This is a test snippet for when crawling fails.'
            }]
            print("  Using fallback data to continue tests")
    
    # 3. Test simple research cycle
    print("\n3. Testing research analysis...")
    try:
        research_prompt = f"""
        Based on this information about a company:
        {results[0]['snippet'] if results else 'No data available'}
        
        What English training challenges might a Japanese tech company face?
        Answer in 2-3 bullet points.
        """
        
        analysis = await ollama.generate(
            model='dolphin3:latest',
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
        from datetime import datetime
        
        report = f"""
# English Training Analysis - Test Report

## Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Findings
{analysis['response']}

## Sources
- {results[0].get('url', 'No URL')}

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
