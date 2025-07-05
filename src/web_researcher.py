"""Web research capabilities using Crawl4ai."""

import asyncio
import logging
from typing import Dict, List, Optional

from crawl4ai import AsyncWebCrawler, LLMExtractionStrategy
from ollama import AsyncClient

logger = logging.getLogger(__name__)


class WebResearcher:
    """Handles web searching and content extraction."""
    
    def __init__(self):
        """Initialize the web researcher."""
        self.crawler = None
        self.ollama = AsyncClient()
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.crawler = AsyncWebCrawler()
        await self.crawler.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.crawler:
            await self.crawler.close()
            
    async def search_and_analyze(self, query: str, priority_sources: List[str]) -> List[Dict]:
        """Search the web and analyze results."""
        if not self.crawler:
            self.crawler = AsyncWebCrawler()
            await self.crawler.start()
            
        findings = []
        
        try:
            # Perform web search
            search_results = await self.crawler.search(query, max_results=10)
            
            # Evaluate and analyze top results
            for result in search_results[:5]:
                quality = await self.evaluate_source(result)
                
                if quality >= 7:  # High quality threshold
                    # Extract content from the page
                    content = await self.extract_content(result['url'], query)
                    
                    if content:
                        findings.append({
                            'url': result['url'],
                            'title': result.get('title', ''),
                            'quality_score': quality,
                            'key_insight': content['insight'],
                            'relevant_text': content['text'][:500],
                            'query': query
                        })
                        
        except Exception as e:
            logger.error(f"Error in search_and_analyze: {e}")
            
        return findings
        
    async def evaluate_source(self, result: Dict) -> int:
        """Evaluate the quality of a search result."""
        prompt = f"""
        Evaluate this search result quality on a scale of 1-10:
        
        URL: {result.get('url', '')}
        Title: {result.get('title', '')}
        Snippet: {result.get('snippet', '')[:200]}
        
        Consider:
        - Is this a primary source or aggregator?
        - How relevant is it to research?
        - Is it recent and authoritative?
        
        Respond with just a number 1-10.
        """
        
        try:
            response = await self.ollama.generate(
                model='dolphin-llama3:8b',
                prompt=prompt
            )
            
            # Extract number from response
            score_text = response['response'].strip()
            score = int(''.join(filter(str.isdigit, score_text)) or '5')
            return min(max(score, 1), 10)  # Ensure 1-10 range
            
        except:
            return 5  # Default middle score
            
    async def extract_content(self, url: str, query: str) -> Optional[Dict]:
        """Extract relevant content from a webpage."""
        try:
            # Use LLM extraction strategy
            extraction_strategy = LLMExtractionStrategy(
                model='dolphin-llama3:8b',
                instruction=f"Extract information relevant to: {query}"
            )
            
            # Crawl the page
            result = await self.crawler.crawl(
                url,
                extraction_strategy=extraction_strategy
            )
            
            if result and result.extracted_content:
                # Analyze the extracted content
                analysis_prompt = f"""
                Based on this content about '{query}':
                
                {result.extracted_content[:2000]}
                
                Provide:
                1. One key insight (1-2 sentences)
                2. Why this matters for research
                
                Format:
                INSIGHT: [your insight]
                RELEVANCE: [why it matters]
                """
                
                response = await self.ollama.generate(
                    model='dolphin-llama3:8b',
                    prompt=analysis_prompt
                )
                
                return {
                    'text': result.extracted_content,
                    'insight': response['response'].split('INSIGHT:')[1].split('RELEVANCE:')[0].strip()
                    if 'INSIGHT:' in response['response'] else 'No clear insight extracted'
                }
                
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            
        return None