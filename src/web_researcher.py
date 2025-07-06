"""Web research capabilities using Crawl4ai and Brave Search."""

import asyncio
import logging
from typing import Dict, List, Optional
import yaml
import json
import httpx

from crawl4ai import AsyncWebCrawler
from ollama import AsyncClient

logger = logging.getLogger(__name__)


class WebResearcher:
    """Handles web searching and content extraction."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the web researcher."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.ollama = AsyncClient()
        self.model = self.config['ollama']['model']  # Get model from config
        
        # Store API key for direct requests
        self.brave_api_key = self.config.get('brave_search', {}).get('api_key')
        if self.brave_api_key and self.brave_api_key != 'YOUR_ACTUAL_BRAVE_API_KEY_HERE':
            logger.info("Brave Search API key configured")
        else:
            self.brave_api_key = None
            logger.warning("Brave Search not configured - using fallback URLs")
        
    async def search_brave_direct(self, query: str, count: int = 10) -> List[Dict]:
        """Make direct HTTP request to Brave Search API to avoid validation issues."""
        if not self.brave_api_key:
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={
                        "q": query,
                        "count": count,
                        "offset": 0,
                        "safesearch": "moderate",
                        "freshness": "pw"  # Past week for recent content
                    },
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": self.brave_api_key
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    urls = []
                    
                    # Extract web results
                    web_results = data.get('web', {}).get('results', [])
                    logger.info(f"Brave Search returned {len(web_results)} results")
                    
                    for result in web_results[:count]:
                        # Ensure URL has protocol
                        url = result.get('url', '')
                        if url and not url.startswith(('http://', 'https://')):
                            url = f"https://{url}"
                            
                        urls.append({
                            'url': url,
                            'title': result.get('title', ''),
                            'description': result.get('description', '')
                        })
                    
                    return urls
                else:
                    logger.error(f"Brave Search API error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Brave Search request error: {e}")
            return []
        
    async def search_and_analyze(self, query: str, priority_sources: List[str]) -> List[Dict]:
        """Search the web and analyze results."""
        findings = []
        urls = []
        
        # Try to search with Brave
        if self.brave_api_key:
            urls = await self.search_brave_direct(query, count=8)
            if not urls:
                logger.warning("Brave Search returned no results, using fallback")
                urls = await self._get_fallback_urls(query)
        else:
            # Use fallback URLs if Brave Search not available
            urls = await self._get_fallback_urls(query)
            
        # Crawl and analyze each URL
        async with AsyncWebCrawler(verbose=True) as crawler:
            for url_info in urls[:5]:  # Limit to 5 URLs per search to avoid overwhelming
                if not url_info.get('url'):  # Skip if no URL
                    continue
                    
                try:
                    logger.info(f"Crawling: {url_info['url']}")
                    # Crawl the page with better settings for dynamic content
                    result = await crawler.arun(
                        url=url_info['url'],
                        word_count_threshold=100,  # Minimum words to consider
                        remove_overlay_elements=True  # Remove popups/overlays
                    )
                    
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
                        
                        # Lower threshold for known good sources
                        threshold = 5 if any(site in url_info['url'].lower() 
                                           for site in ['glassdoor', 'linkedin', 'indeed', 'tokyodev']) else 6
                        
                        if relevance >= threshold:
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
                                logger.info(f"Extracted findings from {url_info['url']}")
                            else:
                                logger.info(f"No relevant findings in {url_info['url']}")
                        else:
                            logger.info(f"Content not relevant enough: {url_info['url']} (score: {relevance})")
                            
                except Exception as e:
                    logger.error(f"Error crawling {url_info['url']}: {e}")
                    
        return findings
        
    async def quick_relevance_check(self, content: str, query: str, title: str) -> int:
        """Quick check if content is relevant to the query."""
        # More lenient prompt for better relevance detection
        prompt = f"""
        Rate how relevant this content is to the query "{query}" on a scale of 1-10.
        
        Page title: {title}
        Content preview:
        {content[:1500]}
        
        Consider:
        - Does it mention topics related to the query?
        - Could it potentially contain useful information?
        - Is there actual content (not just navigation)?
        
        Be generous - if it might be relevant, score it 6 or higher.
        Sites like Glassdoor, LinkedIn, Indeed are usually relevant for company research.
        
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
        You are a research assistant extracting specific information about Japanese tech companies and English training.
        
        From this content, extract ANY mentions of:
        1. Company names (especially Japanese ones like Rakuten, Mercari, LINE, etc.)
        2. English language challenges in the workplace
        3. Corporate training programs or English learning solutions
        4. Names and job titles of HR or training professionals
        5. Information about global expansion or international offices
        6. Employee comments about English or language barriers
        7. Budget or investment in English training
        8. Dates or timelines
        
        Content to analyze:
        {content[:10000]}
        
        Instructions:
        - Extract ACTUAL information from the content, not generic statements
        - Include specific names, numbers, quotes when available
        - If this is a job listing page, extract company names from the listings
        - If this is a review site, extract company names and employee feedback
        
        Return a JSON object with these exact keys:
        {{
            "companies": ["list of company names found, with brief context"],
            "english_challenges": ["specific challenges mentioned"],
            "current_solutions": ["training programs or tools mentioned"],
            "decision_makers": ["names and titles found"],
            "expansion_info": ["global expansion details"],
            "employee_feedback": ["quotes or comments about English"],
            "budget_info": ["financial information"],
            "key_insights": ["2-3 specific insights from this content"],
            "relevant_findings": true/false
        }}
        
        Set relevant_findings to true if you found ANY useful information.
        If the content has no relevant information, return all empty arrays and set relevant_findings to false.
        """
        
        try:
            response = await self.ollama.generate(
                model=self.model,
                prompt=prompt,
                options={'temperature': 0.3}  # Lower temperature for more factual extraction
            )
            
            # Parse JSON response
            try:
                # Clean up the response - sometimes LLMs add extra text
                response_text = response['response'].strip()
                # Find JSON in the response
                if '{' in response_text and '}' in response_text:
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    json_text = response_text[start:end]
                    extracted = json.loads(json_text)
                else:
                    extracted = json.loads(response_text)
                
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
                
                # Log what we found
                if extracted['relevant_findings']:
                    logger.info(f"Extracted from {url}: {len(extracted.get('companies', []))} companies, "
                               f"{len(extracted.get('english_challenges', []))} challenges")
                
                return extracted
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON extraction from {url}: {e}")
                logger.error(f"Raw response: {response['response'][:200]}...")
                return {'relevant_findings': False}
                
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return {'relevant_findings': False}
            
    async def _get_fallback_urls(self, query: str) -> List[Dict]:
        """Get fallback URLs when Brave Search is not available."""
        logger.info("Using fallback URLs")
        
        # More diverse fallback URLs
        if "japanese" in query.lower() or "japan" in query.lower():
            return [
                {
                    'url': "https://www.tokyodev.com/companies/",
                    'title': "Tech Companies in Tokyo - TokyoDev",
                    'description': "List of technology companies in Tokyo"
                },
                {
                    'url': "https://www.japan-dev.com/companies",
                    'title': "Japan Dev - Tech Companies",
                    'description': "Japanese tech companies hiring developers"
                },
                {
                    'url': "https://www.glassdoor.com/Reviews/japan-reviews-SRCH_IL.0,5_IN123.htm",
                    'title': "Companies in Japan Reviews - Glassdoor",
                    'description': "Employee reviews of companies in Japan"
                },
                {
                    'url': "https://www.linkedin.com/jobs/english-jobs-japan/",
                    'title': "English Jobs in Japan - LinkedIn",
                    'description': "Jobs requiring English in Japan"
                },
                {
                    'url': "https://resources.realestate.co.jp/living/10-major-companies-in-japan/",
                    'title': "10 Major Companies in Japan",
                    'description': "Overview of major Japanese companies"
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
