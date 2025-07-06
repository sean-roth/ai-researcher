"""Web research capabilities using Crawl4ai and Brave Search."""

import asyncio
import logging
from typing import Dict, List, Optional
import yaml

from crawl4ai import AsyncWebCrawler
from ollama import AsyncClient

try:
    from brave import AsyncBrave
    BRAVE_AVAILABLE = True
except ImportError:
    BRAVE_AVAILABLE = False
    logging.warning("brave-search not installed. Install with: pip install brave-search")

logger = logging.getLogger(__name__)


class WebResearcher:
    """Handles web searching and content extraction."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the web researcher."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.ollama = AsyncClient()
        
        # Initialize Brave Search if available and configured
        if BRAVE_AVAILABLE and 'brave_search' in self.config and self.config['brave_search'].get('api_key'):
            self.brave = AsyncBrave(api_key=self.config['brave_search']['api_key'])
            logger.info("Brave Search initialized successfully")
        else:
            self.brave = None
            logger.warning("Brave Search not available - using fallback URLs")
        
    async def search_and_analyze(self, query: str, priority_sources: List[str]) -> List[Dict]:
        """Search the web and analyze results."""
        findings = []
        urls = []
        
        # Try to search with Brave
        if self.brave:
            try:
                # Perform search
                search_results = await self.brave.search(q=query, count=10)
                
                # Extract URLs from search results
                if hasattr(search_results, 'web_results') and search_results.web_results:
                    for result in search_results.web_results[:5]:  # Take top 5
                        urls.append({
                            'url': result.url,
                            'title': result.title,
                            'description': result.description if hasattr(result, 'description') else ''
                        })
                    logger.info(f"Found {len(urls)} results for query: {query}")
                else:
                    logger.warning("No web results found")
                    
            except Exception as e:
                logger.error(f"Brave Search error: {e}")
                # Fall back to example URLs
                urls = await self._get_fallback_urls(query)
        else:
            # Use fallback URLs if Brave Search not available
            urls = await self._get_fallback_urls(query)
            
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
            
    async def _get_fallback_urls(self, query: str) -> List[Dict]:
        """Get fallback URLs when Brave Search is not available."""
        logger.info("Using fallback URLs")
        
        # Return some general URLs that might have relevant content
        if "japanese" in query.lower() or "japan" in query.lower():
            return [
                {
                    'url': "https://www.japan-dev.com/",
                    'title': "Japan Dev - Tech Jobs in Japan",
                    'description': "Resources for developers in Japan"
                },
                {
                    'url': "https://www.tokyodev.com/",
                    'title': "TokyoDev - Developer Jobs in Tokyo",
                    'description': "Tokyo developer community and job board"
                }
            ]
        else:
            return [
                {
                    'url': "https://www.example.com",
                    'title': "Example Domain",
                    'description': "Example site for testing"
                }
            ]
