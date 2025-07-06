"""Web research capabilities using Crawl4ai."""

import asyncio
import logging
from typing import Dict, List, Optional

from crawl4ai import AsyncWebCrawler
from ollama import AsyncClient

logger = logging.getLogger(__name__)


class WebResearcher:
    """Handles web searching and content extraction."""
    
    def __init__(self):
        """Initialize the web researcher."""
        self.ollama = AsyncClient()
        
    async def search_and_analyze(self, query: str, priority_sources: List[str]) -> List[Dict]:
        """Search the web and analyze results."""
        findings = []
        
        # For now, we'll crawl a few known sites based on the query
        # In a real implementation, you'd integrate with a search API
        test_urls = [
            "https://www.example.com",
            "https://en.wikipedia.org/wiki/English_as_a_second_or_foreign_language"
        ]
        
        async with AsyncWebCrawler(verbose=True) as crawler:
            for url in test_urls[:2]:  # Limit to 2 URLs for testing
                try:
                    # Crawl the page
                    result = await crawler.arun(url=url)
                    
                    if result.success and result.markdown:
                        # Evaluate if content is relevant
                        quality = await self.evaluate_content(result.markdown[:1000], query)
                        
                        if quality >= 7:
                            # Extract insights
                            insight = await self.extract_insight(result.markdown[:2000], query)
                            
                            findings.append({
                                'url': url,
                                'title': result.title or 'No title',
                                'quality_score': quality,
                                'key_insight': insight,
                                'relevant_text': result.markdown[:500],
                                'query': query
                            })
                            
                except Exception as e:
                    logger.error(f"Error crawling {url}: {e}")
                    
        return findings
        
    async def evaluate_content(self, content: str, query: str) -> int:
        """Evaluate if content is relevant to the query."""
        prompt = f"""
        Rate how relevant this content is to the query "{query}" on a scale of 1-10:
        
        Content preview:
        {content[:500]}
        
        Consider:
        - Does it directly address the query topic?
        - Is it informative and substantive?
        - Is it from a credible source?
        
        Respond with just a number 1-10.
        """
        
        try:
            response = await self.ollama.generate(
                model='dolphin3:latest',
                prompt=prompt
            )
            
            # Extract number from response
            score_text = response['response'].strip()
            score = int(''.join(filter(str.isdigit, score_text)) or '5')
            return min(max(score, 1), 10)  # Ensure 1-10 range
            
        except Exception as e:
            logger.error(f"Error evaluating content: {e}")
            return 5  # Default middle score
            
    async def extract_insight(self, content: str, query: str) -> str:
        """Extract a key insight from the content."""
        prompt = f"""
        Based on this content about '{query}':
        
        {content[:1500]}
        
        Provide one key insight (1-2 sentences) that would be valuable for research.
        Be specific and actionable.
        """
        
        try:
            response = await self.ollama.generate(
                model='dolphin3:latest',
                prompt=prompt
            )
            
            return response['response'].strip()
            
        except Exception as e:
            logger.error(f"Error extracting insight: {e}")
            return "Unable to extract clear insight from this source"
