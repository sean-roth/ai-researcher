"""Core research engine for the AI Researcher."""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

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
        
        # Execute research cycles
        all_findings = []
        for cycle in range(min(strategy['cycles'], self.config['research']['max_cycles'])):
            logger.info(f"Starting research cycle {cycle + 1}")
            
            # Execute research
            findings = await self.research_cycle(strategy, all_findings)
            all_findings.extend(findings)
            
            # Checkpoint progress
            await self.checkpoint(assignment, all_findings, cycle)
            
            # Refine strategy based on findings
            strategy = await self.refine_strategy(strategy, all_findings)
            
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
        
        Develop a research strategy:
        1. What are the key questions to answer?
        2. What search queries will be most effective?
        3. How many research cycles are needed?
        4. What sources should be prioritized?
        
        Respond in JSON format with keys:
        - approach: brief strategy description
        - key_questions: list of specific questions
        - search_queries: list of initial queries
        - cycles: number of research cycles (1-5)
        - priority_sources: list of source types to focus on
        """
        
        response = await self.ollama.generate(
            model=self.config['ollama']['model'],
            prompt=prompt
        )
        
        # Parse JSON response
        try:
            strategy = json.loads(response['response'])
        except:
            # Fallback strategy if parsing fails
            strategy = {
                'approach': 'Comprehensive web research',
                'key_questions': assignment['objectives'],
                'search_queries': [obj.split()[:3] for obj in assignment['objectives']],
                'cycles': 3,
                'priority_sources': ['corporate sites', 'news', 'forums']
            }
            
        return strategy
        
    async def research_cycle(self, strategy: Dict, previous_findings: List) -> List[Dict]:
        """Execute one research cycle."""
        findings = []
        
        # Generate search queries based on strategy and previous findings
        queries = await self.generate_queries(strategy, previous_findings)
        
        # Execute searches
        for query in queries[:5]:  # Limit queries per cycle
            results = await self.web_researcher.search_and_analyze(
                query, 
                strategy['priority_sources']
            )
            findings.extend(results)
            
        return findings
        
    async def generate_queries(self, strategy: Dict, previous_findings: List) -> List[str]:
        """Generate search queries based on strategy and findings."""
        if not previous_findings:
            return strategy['search_queries']
            
        # Use LLM to generate new queries based on what we've learned
        findings_summary = self.summarize_findings(previous_findings[:10])
        
        prompt = f"""
        Research strategy: {strategy['approach']}
        Key questions: {json.dumps(strategy['key_questions'])}
        
        What we've learned so far:
        {findings_summary}
        
        Generate 5 new search queries to dig deeper or explore new angles.
        Return as a JSON array of strings.
        """
        
        response = await self.ollama.generate(
            model=self.config['ollama']['model'],
            prompt=prompt
        )
        
        try:
            queries = json.loads(response['response'])
            return queries
        except:
            # Fallback to variations of original queries
            return [q + " 2024" for q in strategy['search_queries'][:5]]
            
    async def refine_strategy(self, strategy: Dict, findings: List) -> Dict:
        """Refine strategy based on findings."""
        # For now, keep strategy mostly the same
        # In future, could adjust based on what we're finding
        return strategy
        
    async def checkpoint(self, assignment: Dict, findings: List, cycle: int):
        """Save checkpoint for crash recovery."""
        checkpoint = {
            'assignment': assignment,
            'findings': findings,
            'cycle': cycle,
            'timestamp': datetime.now().isoformat()
        }
        
        checkpoint_path = Path('checkpoints') / f"{assignment['title'][:30]}_{cycle}.json"
        checkpoint_path.parent.mkdir(exist_ok=True)
        
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)
            
    def summarize_findings(self, findings: List[Dict]) -> str:
        """Create a brief summary of findings."""
        summary_parts = []
        for finding in findings[:5]:
            summary_parts.append(
                f"- {finding.get('title', 'Unknown')}: {finding.get('key_insight', 'No insight')[:100]}"
            )
        return "\n".join(summary_parts)
