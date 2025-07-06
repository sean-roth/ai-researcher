"""Web research capabilities using Crawl4ai and Brave Search."""

import asyncio
import logging
from typing import Dict, List, Optional
import yaml

from crawl4ai import AsyncWebCrawler
from ollama import AsyncClient
from brave import AsyncBrave

logger = logging.getLogger(__name__)


class WebResearcher:
    """Handles web searching and content extraction."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the web researcher."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.ollama = AsyncClient()
        self.brave = AsyncBrave(api_key=self.config['brave_search']['api_key'])
        
    async def search_and_analyze(self, query: str, priority_sources: List[str]) -> List[Dict]:
        """Search the web and analyze results."""
        findings = []
        
        try:
            # Search with Brave
            search_results = await self.brave.search(
                q=query,
                count=10  # Get 10 results
            )
            
            # Extract URLs from search results
            urls = []
            if hasattr(search_results, 'web_results'):
                for result in search_results.web_results[:5]:  # Take top 5
                    urls.append({
                        'url': result.url,
                        'title': result.title,
                        'description': result.description
                    })
            
            # Crawl and analyze each URL
            async with AsyncWebCrawler(verbose=True) as crawler:
                for url_info in urls:
                    try:
                        # Crawl the page
                        result = await crawler.arun(url=url_info['url'])
                        
                        if result.success and result.markdown:
                            # Evaluate if content is relevant
                            quality = await self.evaluate_content(
                                result.markdown[:1000], 
                                query,
                                url_info['title']
                            )
                            
                            if quality >= 7:
                                # Extract insights
                                insight = await self.extract_insight(
                                    result.markdown[:2000], 
                                    query
                                )
                                
                                findings.append({
                                    'url': url_info['url'],
                                    'title': url_info['title'],
                                    'quality_score': quality,
                                    'key_insight': insight,
                                    'relevant_text': result.markdown[:500],
                                    'query': query
                                })
                                
                    except Exception as e:
                        logger.error(f"Error crawling {url_info['url']}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in search_and_analyze: {e}")
            # Fallback to example URLs if search fails
            logger.info("Falling back to example URLs")
            findings = await self._fallback_search(query)
                    
        return findings
        
    async def evaluate_content(self, content: str, query: str, title: str) -> int:
        """Evaluate if content is relevant to the query."""
        prompt = f"""
        Rate how relevant this content is to the query "{query}" on a scale of 1-10:
        
        Page title: {title}
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
            
    async def _fallback_search(self, query: str) -> List[Dict]:
        """Fallback search using known URLs if Brave Search fails."""
        test_urls = [
            {
                'url': "https://www.example.com",
                'title': "Example Domain",
                'description': "Example site for testing"
            }
        ]
        
        findings = []
        async with AsyncWebCrawler(verbose=True) as crawler:
            for url_info in test_urls:
                try:
                    result = await crawler.arun(url=url_info['url'])
                    if result.success:
                        findings.append({
                            'url': url_info['url'],
                            'title': url_info['title'],
                            'quality_score': 5,
                            'key_insight': "Fallback result - search API not configured",
                            'relevant_text': result.markdown[:200] if result.markdown else "",
                            'query': query
                        })
                except Exception as e:
                    logger.error(f"Fallback crawl error: {e}")
                    
        return findings
