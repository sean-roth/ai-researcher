"""
Integration layer between Aria and the Research Engine.
Enables real-time observations and progress updates.
"""

import asyncio
from typing import Dict, List, Optional, Callable
from pathlib import Path
import yaml
import json

from src.research_engine import ResearchEngine
from aria_core.aria_personality import AriaPersonality


class AriaResearchIntegration:
    """Connects Aria's personality to the research engine."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.research_engine = ResearchEngine(config_path)
        self.personality = AriaPersonality()
        self.progress_callback = None
        self.observation_callback = None
        
        # Track patterns for observations
        self.pattern_tracker = {
            'companies_by_location': {},
            'companies_by_size': {},
            'timing_patterns': [],
            'common_challenges': {},
            'solution_providers': {}
        }
        
    async def process_with_observations(self, assignment_path: Path, 
                                      progress_callback: Optional[Callable] = None,
                                      observation_callback: Optional[Callable] = None):
        """Process research assignment with Aria's observations."""
        self.progress_callback = progress_callback
        self.observation_callback = observation_callback
        
        # Patch the research engine to intercept findings
        original_update = self.research_engine._update_found_entities
        self.research_engine._update_found_entities = self._update_with_observations
        
        try:
            # Run research
            reports = await self.research_engine.process_assignment(assignment_path)
            
            # Final observation
            await self._make_final_observation()
            
            return reports
            
        finally:
            # Restore original method
            self.research_engine._update_found_entities = original_update
    
    def _update_with_observations(self, findings: List[Dict]):
        """Intercept entity updates to make observations."""
        # Call original update
        self.research_engine.__class__._update_found_entities(self.research_engine, findings)
        
        # Analyze for patterns
        asyncio.create_task(self._analyze_findings(findings))
    
    async def _analyze_findings(self, findings: List[Dict]):
        """Analyze findings for interesting patterns."""
        for finding in findings:
            if 'extracted_data' not in finding:
                continue
                
            data = finding['extracted_data']
            
            # Track locations
            if data.get('companies'):
                for company in data['companies']:
                    if isinstance(company, dict):
                        location = company.get('location', 'Unknown')
                        self.pattern_tracker['companies_by_location'][location] = \
                            self.pattern_tracker['companies_by_location'].get(location, 0) + 1
                        
                        # Check for location cluster
                        if self.pattern_tracker['companies_by_location'][location] >= 3:
                            await self._make_observation({
                                'pattern_count': self.pattern_tracker['companies_by_location'][location],
                                'detail': f"{location} seems to be a hub - {self.pattern_tracker['companies_by_location'][location]} companies there",
                                'pattern': f"concentration in {location}"
                            })
            
            # Track timing patterns
            if 'recent' in str(data).lower() or '2025' in str(data):
                self.pattern_tracker['timing_patterns'].append(finding.get('title', ''))
                
                if len(self.pattern_tracker['timing_patterns']) >= 3:
                    await self._make_observation({
                        'time_correlation': True,
                        'detail': "lot of recent activity - might be industry-wide push",
                        'timeframe': "the past few months"
                    })
            
            # Track challenges
            if data.get('english_challenges'):
                for challenge in data['english_challenges']:
                    challenge_str = str(challenge).lower()
                    self.pattern_tracker['common_challenges'][challenge_str] = \
                        self.pattern_tracker['common_challenges'].get(challenge_str, 0) + 1
            
            # Detect outliers
            if data.get('companies'):
                for company in data['companies']:
                    if isinstance(company, dict):
                        # Small company with big ambitions
                        if company.get('size', 1000) < 100 and 'global' in str(company).lower():
                            await self._make_observation({
                                'is_outlier': True,
                                'company': company.get('name', 'A company'),
                                'reason': "small size but global ambitions"
                            })
    
    async def _make_observation(self, context: Dict):
        """Make an observation through Aria's personality."""
        observation = self.personality.make_observation(context)
        
        if observation and self.observation_callback:
            await self.observation_callback(observation)
    
    async def _make_final_observation(self):
        """Make final observations about the research."""
        # Most common location
        if self.pattern_tracker['companies_by_location']:
            top_location = max(self.pattern_tracker['companies_by_location'].items(), 
                             key=lambda x: x[1])
            if top_location[1] > 5:
                await self._make_observation({
                    'pattern_count': top_location[1],
                    'detail': f"Strong concentration in {top_location[0]} - {top_location[1]} companies",
                    'pattern': "geographic clustering"
                })
        
        # Common challenges
        if self.pattern_tracker['common_challenges']:
            top_challenge = max(self.pattern_tracker['common_challenges'].items(),
                              key=lambda x: x[1])
            if top_challenge[1] > 3:
                await self._make_observation({
                    'significance': 0.8,
                    'hypothesis': f"'{top_challenge[0]}' is the main pain point",
                    'count': top_challenge[1]
                })
    
    def get_progress_stats(self) -> Dict:
        """Get current research progress statistics."""
        return {
            'companies_found': len(self.research_engine.found_entities.get('companies', [])),
            'people_found': len(self.research_engine.found_entities.get('decision_makers', [])),
            'locations_covered': len(self.pattern_tracker['companies_by_location']),
            'patterns_detected': sum([
                len(self.pattern_tracker['companies_by_location']) > 3,
                len(self.pattern_tracker['timing_patterns']) > 3,
                len(self.pattern_tracker['common_challenges']) > 2
            ])
        }
