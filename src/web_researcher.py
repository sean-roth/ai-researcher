"""Web research capabilities using Crawl4ai and Brave Search."""

import asyncio
import logging
from typing import Dict, List, Optional
import yaml
import json

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
        self.model = self.config['ollama']['model']  # Get model from config
        
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
                    for result in search_results.web_results[:8]:  # Take top 8 results
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
            for url_info in urls[:5]:  # Limit to 5 URLs per search to avoid overwhelming
                try:
                    logger.info(f"Crawling: {url_info['url']}")
                    # Crawl the page
                    result = await crawler.arun(url=url_info['url'])
                    
                    if result.success and result.markdown:
                        # Use full content for evaluation (but cap at reasonable limit)
                        content_length = len(result.markdown)
                        logger.info(f"Crawled {content_length} characters from {url_info['url']}")
                        
                        # First quick relevance check on preview
                        relevance = await self.quick_relevance_check(
                            result.markdown[:3000], 
                            query,
                            url_info['title']
                        )
                        
                        if relevance >= 6:
                            # Extract structured data from full content
                            extracted_data = await self.extract_structured_data(
                                result.markdown[:15000],  # Use much more content
                                query,
                                url_info['url']
                            )
                            
                            if extracted_data and extracted_data.get('relevant_findings'):
                                findings.append({
                                    'url': url_info['url'],
                                    'title': url_info['title'],
                                    'quality_score': relevance,
                                    'extracted_data': extracted_data,
                                    'content_length': content_length,
                                    'query': query
                                })
                            else:
                                logger.info(f"No relevant findings in {url_info['url']}")
                        else:
                            logger.info(f"Content not relevant enough: {url_info['url']} (score: {relevance})")
                            
                except Exception as e:
                    logger.error(f"Error crawling {url_info['url']}: {e}")
                    
        return findings
        
    async def quick_relevance_check(self, content: str, query: str, title: str) -> int:
        """Quick check if content is relevant to the query."""
        prompt = f"""
        Rate how relevant this content is to the query "{query}" on a scale of 1-10:
        
        Page title: {title}
        Content preview:
        {content[:1500]}
        
        Consider:
        - Does it directly address the query topic?
        - Is it substantive (not just navigation/ads)?
        - Does it contain specific information (names, data, facts)?
        
        Respond with just a number 1-10.
        """
        
        try:
            response = await self.ollama.generate(
                model=self.model,
                prompt=prompt
            )
            
            # Extract number from response
            score_text = response['response'].strip()
            score = int(''.join(filter(str.isdigit, score_text)) or '5')
            return min(max(score, 1), 10)  # Ensure 1-10 range
            
        except Exception as e:
            logger.error(f"Error evaluating content: {e}")
            return 5  # Default middle score
            
    async def extract_structured_data(self, content: str, query: str, url: str) -> Dict:
        """Extract structured data from the content."""
        prompt = f"""
        Extract specific, factual information from this content related to: "{query}"
        
        Content:
        {content}
        
        Extract the following (if available):
        1. Company names mentioned (especially Japanese tech companies)
        2. Specific English challenges or pain points mentioned
        3. Training programs or solutions currently used
        4. Names and titles of decision makers (HR, Training, L&D)
        5. Recent expansions or global initiatives
        6. Employee quotes or testimonials about English
        7. Budget information or training investments
        8. Specific dates or timelines
        
        Return as JSON with these keys:
        - companies: [list of company names with context]
        - english_challenges: [specific challenges mentioned]
        - current_solutions: [training programs or tools mentioned]
        - decision_makers: [names and titles]
        - expansion_info: [global expansion details]
        - employee_feedback: [quotes or feedback]
        - budget_info: [any financial information]
        - key_insights: [2-3 specific, actionable insights]
        - relevant_findings: true/false (whether any useful info was found)
        
        Be specific - include names, numbers, quotes. Don't summarize, extract.
        """
        
        try:
            response = await self.ollama.generate(
                model=self.model,
                prompt=prompt,
                options={'temperature': 0.3}  # Lower temperature for more factual extraction
            )
            
            # Parse JSON response
            try:
                extracted = json.loads(response['response'])
                # Ensure we have the relevant_findings flag
                if 'relevant_findings' not in extracted:
                    # Check if we found anything useful
                    has_findings = any([
                        extracted.get('companies'),
                        extracted.get('english_challenges'),
                        extracted.get('current_solutions'),
                        extracted.get('decision_makers')
                    ])
                    extracted['relevant_findings'] = has_findings
                return extracted
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON extraction from {url}")
                return {'relevant_findings': False}
                
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return {'relevant_findings': False}
            
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
                },
                {
                    'url': "https://www.glassdoor.com/Reviews/japan-tech-company-reviews-SRCH_IL.0,5_IN123_KE6,10.htm",
                    'title': "Tech Company Reviews in Japan - Glassdoor",
                    'description': "Employee reviews of tech companies in Japan"
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
