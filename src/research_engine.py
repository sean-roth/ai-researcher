"""Core research engine for the AI Researcher."""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from ollama import AsyncClient

from .web_researcher import WebResearcher
from .report_writer import ReportWriter

logger = logging.getLogger(__name__)


class ResearchEngine:
    """Main research orchestration engine."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the research engine with configuration."""
        self.config_path = config_path
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.ollama = AsyncClient(
            host=f"{self.config['ollama']['host']}:{self.config['ollama']['port']}"
        )
        self.web_researcher = WebResearcher(config_path)
        self.report_writer = ReportWriter()
        self.checkpoint_data = {}
        
    async def process_assignment(self, assignment_path: Path) -> List[Path]:
        """Process a research assignment and generate reports."""
        logger.info(f"Processing assignment: {assignment_path}")
        
        # Load assignment
        with open(assignment_path, 'r') as f:
            assignment = yaml.safe_load(f)
            
        # Develop research strategy
        strategy = await self.develop_strategy(assignment)
        logger.info(f"Strategy developed: {strategy['approach']}")
        
        # Initialize tracking for found entities
        self.found_entities = {
            'companies': set(),
            'decision_makers': set(),
            'solutions': set(),
            'challenges': set()
        }
        
        # Execute research cycles
        all_findings = []
        for cycle in range(min(strategy['cycles'], self.config['research']['max_cycles'])):
            logger.info(f"Starting research cycle {cycle + 1}")
            
            # Execute research
            findings = await self.research_cycle(strategy, all_findings, cycle)
            all_findings.extend(findings)
            
            # Update our entity tracking
            self._update_found_entities(findings)
            
            # Checkpoint progress
            await self.checkpoint(assignment, all_findings, cycle)
            
            # Refine strategy based on findings
            strategy = await self.refine_strategy(strategy, all_findings, assignment)
            
            # Log progress
            logger.info(f"Cycle {cycle + 1} complete. Found {len(self.found_entities['companies'])} companies, "
                       f"{len(self.found_entities['decision_makers'])} decision makers")
            
        # Generate final reports
        reports = await self.report_writer.generate_reports(
            assignment, all_findings, strategy
        )
        
        return reports
        
    async def develop_strategy(self, assignment: Dict) -> Dict:
        """Develop a research strategy based on the assignment."""
        prompt = f"""
        Research Assignment: {assignment['title']}
        Objectives: {json.dumps(assignment['objectives'], indent=2)}
        Depth: {assignment.get('depth', 'comprehensive')}
        
        Develop a comprehensive research strategy that will find specific companies, people, and solutions.
        
        Consider these search angles:
        1. Direct company searches (e.g., "Japanese tech companies global expansion 2024 2025")
        2. Industry reports and news (e.g., "Japan IT companies English training investment")
        3. Employee review sites (e.g., "Glassdoor Japanese tech company English communication")
        4. LinkedIn searches (e.g., "HR director Japanese technology company English training")
        5. Case studies and success stories (e.g., "corporate English training Japan case study")
        6. Forums and discussions (e.g., "reddit working Japanese tech company English")
        
        Respond in JSON format with keys:
        - approach: detailed strategy description (2-3 sentences)
        - key_questions: list of specific questions to answer
        - search_queries: list of 10-15 diverse, specific search queries (as strings)
        - cycles: number of research cycles (3-5 for comprehensive)
        - priority_sources: list of source types to focus on
        """
        
        response = await self.ollama.generate(
            model=self.config['ollama']['model'],
            prompt=prompt,
            options={'temperature': 0.7}
        )
        
        # Parse JSON response
        try:
            strategy = json.loads(response['response'])
            # Ensure we have good search queries
            if len(strategy.get('search_queries', [])) < 5:
                # Generate default queries based on objectives
                strategy['search_queries'] = await self._generate_default_queries(assignment)
        except:
            # Fallback strategy if parsing fails
            strategy = {
                'approach': 'Conduct a comprehensive analysis by researching Japanese tech companies that have recently expanded globally, identifying English communication challenges, discovering current training solutions, and finding decision makers in HR or Training departments.',
                'key_questions': assignment['objectives'],
                'search_queries': await self._generate_default_queries(assignment),
                'cycles': 4,
                'priority_sources': ['corporate sites', 'news articles', 'employee reviews', 'LinkedIn', 'industry reports', 'forums']
            }
            
        return strategy
        
    async def _generate_default_queries(self, assignment: Dict) -> List[str]:
        """Generate default search queries from assignment objectives."""
        queries = [
            # Company-focused searches
            "Japanese tech companies global expansion 2024 2025",
            "Japan IT companies international offices English",
            "Rakuten Mercari LINE global expansion English",
            "Japanese technology firms struggling English communication",
            
            # Employee experience searches
            "Glassdoor reviews Japanese tech companies English skills",
            "working at Japanese tech company English requirements",
            "Japan IT company employee English training reviews",
            
            # Solution-focused searches
            "corporate English training programs Japan technology",
            "business English solutions Japanese companies",
            "English communication training Japanese tech firms",
            
            # Decision maker searches
            "HR director Japanese technology company LinkedIn",
            "chief learning officer Japan tech companies",
            "L&D manager Japanese IT firms English training",
            
            # Industry analysis
            "Japan tech industry English proficiency challenges report",
            "Japanese companies English communication problems study"
        ]
        
        # Add assignment-specific queries
        for obj in assignment.get('objectives', [])[:3]:
            queries.append(f"{obj} Japan 2024 2025")
            
        return queries[:15]  # Limit to 15 queries
        
    async def research_cycle(self, strategy: Dict, previous_findings: List, cycle: int) -> List[Dict]:
        """Execute one research cycle."""
        findings = []
        
        # Generate search queries based on strategy and previous findings
        queries = await self.generate_queries(strategy, previous_findings, cycle)
        
        # Execute searches with rate limiting
        for i, query in enumerate(queries[:5]):  # Limit queries per cycle
            if i > 0:
                # Wait 1.1 seconds between searches to respect Brave's rate limit
                logger.info("Waiting 1.1 seconds for rate limit...")
                await asyncio.sleep(1.1)
            
            # Ensure query is a string
            query_str = self._ensure_string_query(query)
            logger.info(f"Searching for: {query_str}")
            
            results = await self.web_researcher.search_and_analyze(
                query_str, 
                strategy['priority_sources']
            )
            findings.extend(results)
            
        return findings
    
    def _ensure_string_query(self, query: Union[str, Dict, List]) -> str:
        """Ensure the query is a string, extracting from dict/list if needed."""
        if isinstance(query, str):
            return query
        elif isinstance(query, dict):
            # If it's a dict, try to get 'query' key or convert to string
            if 'query' in query:
                return str(query['query'])
            else:
                # Just take the first value that looks like a query
                for k, v in query.items():
                    if isinstance(v, str) and len(v) > 10:
                        return v
                return str(query)
        elif isinstance(query, list):
            # If it's a list, take the first string
            for item in query:
                if isinstance(item, str):
                    return item
            return str(query[0]) if query else "Japanese tech companies"
        else:
            return str(query)
        
    async def generate_queries(self, strategy: Dict, previous_findings: List, cycle: int) -> List[str]:
        """Generate search queries based on strategy and findings."""
        if cycle == 0:
            # First cycle: use initial strategy queries
            return strategy['search_queries'][:5]
        elif cycle == 1:
            # Second cycle: focus on specific companies if found
            if self.found_entities['companies']:
                companies = list(self.found_entities['companies'])[:3]
                return [
                    f"{company} English training program" for company in companies
                ] + [
                    f"{company} HR director LinkedIn" for company in companies[:2]
                ]
            else:
                return strategy['search_queries'][5:10]
        else:
            # Later cycles: dig deeper based on findings
            return await self._generate_deep_queries(strategy, previous_findings)
            
    async def _generate_deep_queries(self, strategy: Dict, previous_findings: List) -> List[str]:
        """Generate queries for deeper research based on findings."""
        # Extract what we've found
        summary = self._create_findings_summary(previous_findings[-10:])  # Last 10 findings
        
        prompt = f"""
        We're researching: {strategy['approach']}
        
        Found so far:
        - Companies: {', '.join(list(self.found_entities['companies'])[:5]) or 'None yet'}
        - Decision makers: {', '.join(list(self.found_entities['decision_makers'])[:3]) or 'None yet'}
        - Solutions mentioned: {', '.join(list(self.found_entities['solutions'])[:3]) or 'None yet'}
        
        Recent findings:
        {summary}
        
        Generate 5 new search queries to:
        1. Find more specific information about companies/people already discovered
        2. Discover new companies we haven't found yet
        3. Find case studies or detailed implementations
        4. Locate budget/investment information
        5. Find employee testimonials or reviews
        
        Make queries specific and actionable. 
        Return ONLY a JSON array of 5 search query strings, nothing else.
        Example: ["query one", "query two", "query three", "query four", "query five"]
        """
        
        response = await self.ollama.generate(
            model=self.config['ollama']['model'],
            prompt=prompt,
            options={'temperature': 0.8}
        )
        
        try:
            # Try to parse the response as JSON
            response_text = response['response'].strip()
            # Find JSON array in the response
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                json_text = response_text[start:end]
                queries = json.loads(json_text)
                
                # Ensure all queries are strings
                string_queries = []
                for q in queries:
                    string_queries.append(self._ensure_string_query(q))
                
                return string_queries[:5]
            else:
                raise ValueError("No JSON array found")
                
        except Exception as e:
            logger.warning(f"Failed to parse query response: {e}")
            # Fallback queries
            if self.found_entities['companies']:
                company = list(self.found_entities['companies'])[0]
                return [
                    f"{company} English training budget investment",
                    f"{company} employee English skills development",
                    "Japanese tech companies English proficiency case study",
                    "corporate language training ROI Japan technology",
                    "English communication challenges Japanese IT firms 2025"
                ]
            else:
                return strategy['search_queries'][10:15]
            
    async def refine_strategy(self, strategy: Dict, findings: List, assignment: Dict) -> Dict:
        """Refine strategy based on findings."""
        # Check progress toward objectives
        companies_found = len(self.found_entities['companies'])
        decision_makers_found = len(self.found_entities['decision_makers'])
        
        # Adjust strategy based on what we need
        if companies_found < 5:
            # Need more companies
            strategy['priority_sources'] = ['news articles', 'industry reports', 'corporate sites']
        elif decision_makers_found < 3:
            # Need more people
            strategy['priority_sources'] = ['LinkedIn', 'corporate sites', 'press releases']
        else:
            # Need more details
            strategy['priority_sources'] = ['case studies', 'employee reviews', 'forums']
            
        return strategy
        
    def _update_found_entities(self, findings: List[Dict]):
        """Update our tracking of found entities."""
        for finding in findings:
            if 'extracted_data' in finding:
                data = finding['extracted_data']
                
                # Add companies
                if data.get('companies'):
                    for company in data['companies']:
                        if isinstance(company, dict):
                            self.found_entities['companies'].add(company.get('name', company.get('company', str(company))))
                        else:
                            self.found_entities['companies'].add(str(company))
                
                # Add decision makers
                if data.get('decision_makers'):
                    for person in data['decision_makers']:
                        if isinstance(person, dict):
                            self.found_entities['decision_makers'].add(
                                f"{person.get('name', 'Unknown')} - {person.get('title', 'Unknown')}"
                            )
                        else:
                            self.found_entities['decision_makers'].add(str(person))
                
                # Add solutions
                if data.get('current_solutions'):
                    for solution in data['current_solutions']:
                        self.found_entities['solutions'].add(str(solution))
                
                # Add challenges
                if data.get('english_challenges'):
                    for challenge in data['english_challenges']:
                        self.found_entities['challenges'].add(str(challenge))
        
    def _create_findings_summary(self, findings: List[Dict]) -> str:
        """Create a summary of recent findings."""
        summary_parts = []
        for finding in findings:
            if 'extracted_data' in finding:
                data = finding['extracted_data']
                insights = data.get('key_insights', [])
                if insights:
                    summary_parts.append(f"From {finding['title']}: {insights[0] if isinstance(insights, list) else insights}")
        return "\n".join(summary_parts) if summary_parts else "No specific insights yet"
        
    async def checkpoint(self, assignment: Dict, findings: List, cycle: int):
        """Save checkpoint for crash recovery."""
        checkpoint = {
            'assignment': assignment,
            'findings': findings,
            'found_entities': {k: list(v) for k, v in self.found_entities.items()},
            'cycle': cycle,
            'timestamp': datetime.now().isoformat()
        }
        
        checkpoint_path = Path('checkpoints') / f"{assignment['title'][:30]}_{cycle}.json"
        checkpoint_path.parent.mkdir(exist_ok=True)
        
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)
