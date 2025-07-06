"""Report generation for research findings."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

import yaml

logger = logging.getLogger(__name__)


class ReportWriter:
    """Generates markdown reports from research findings."""
    
    def __init__(self):
        """Initialize the report writer."""
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, str]:
        """Load report templates."""
        # For now, use embedded templates
        return {
            'bullets': self._bullet_template(),
            'narrative': self._narrative_template(),
            'executive': self._executive_template()
        }
        
    async def generate_reports(self, assignment: Dict, findings: List[Dict], 
                             strategy: Dict) -> List[Path]:
        """Generate reports based on research findings."""
        report_style = assignment.get('report_style', 'bullets')
        output_format = assignment.get('output', {}).get('format', 'single')
        
        reports = []
        
        if output_format == 'single':
            # Generate one comprehensive report
            report = await self._generate_single_report(
                assignment, findings, strategy, report_style
            )
            reports.append(report)
        else:
            # Generate multiple focused reports
            grouped_findings = self._group_findings(findings, assignment)
            
            for group_name, group_findings in grouped_findings.items():
                report = await self._generate_focused_report(
                    assignment, group_findings, group_name, report_style
                )
                reports.append(report)
                
        return reports
        
    async def _generate_single_report(self, assignment: Dict, findings: List[Dict],
                                    strategy: Dict, style: str) -> Path:
        """Generate a single comprehensive report."""
        # Extract structured data from findings
        structured_data = self._extract_all_structured_data(findings)
        
        # Create content sections
        companies_section = self._format_companies(structured_data['companies'])
        challenges_section = self._format_challenges(structured_data['challenges'])
        solutions_section = self._format_solutions(structured_data['solutions'])
        decision_makers_section = self._format_decision_makers(structured_data['decision_makers'])
        insights_section = self._format_key_insights(structured_data['insights'])
        
        # Generate report content
        if style == 'bullets':
            report_content = self._generate_bullet_report(
                assignment, strategy, companies_section, challenges_section,
                solutions_section, decision_makers_section, insights_section,
                findings, structured_data
            )
        else:
            # For now, use bullet format for all styles
            report_content = self._generate_bullet_report(
                assignment, strategy, companies_section, challenges_section,
                solutions_section, decision_makers_section, insights_section,
                findings, structured_data
            )
        
        # Save report
        report_path = Path('output') / f"{assignment['title'][:50]}_{datetime.now():%Y%m%d_%H%M}.md"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report_content)
        
        logger.info(f"Report generated: {report_path}")
        return report_path
        
    def _extract_all_structured_data(self, findings: List[Dict]) -> Dict:
        """Extract all structured data from findings."""
        data = {
            'companies': defaultdict(list),
            'challenges': [],
            'solutions': [],
            'decision_makers': [],
            'insights': [],
            'quotes': [],
            'expansion_info': []
        }
        
        for finding in findings:
            if 'extracted_data' not in finding:
                continue
                
            extracted = finding['extracted_data']
            source_info = {
                'url': finding.get('url', ''),
                'title': finding.get('title', '')
            }
            
            # Extract companies with context
            if extracted.get('companies'):
                for company in extracted['companies']:
                    if isinstance(company, dict):
                        data['companies'][company.get('name', str(company))].append({
                            'context': company.get('context', ''),
                            'source': source_info
                        })
                    else:
                        data['companies'][str(company)].append({
                            'context': '',
                            'source': source_info
                        })
            
            # Extract challenges
            if extracted.get('english_challenges'):
                for challenge in extracted['english_challenges']:
                    data['challenges'].append({
                        'challenge': str(challenge),
                        'source': source_info
                    })
            
            # Extract solutions
            if extracted.get('current_solutions'):
                for solution in extracted['current_solutions']:
                    data['solutions'].append({
                        'solution': str(solution),
                        'source': source_info
                    })
            
            # Extract decision makers
            if extracted.get('decision_makers'):
                for person in extracted['decision_makers']:
                    if isinstance(person, dict):
                        data['decision_makers'].append({
                            'name': person.get('name', 'Unknown'),
                            'title': person.get('title', 'Unknown'),
                            'company': person.get('company', 'Unknown'),
                            'source': source_info
                        })
                    else:
                        data['decision_makers'].append({
                            'info': str(person),
                            'source': source_info
                        })
            
            # Extract insights
            if extracted.get('key_insights'):
                insights = extracted['key_insights']
                if isinstance(insights, list):
                    for insight in insights:
                        data['insights'].append({
                            'insight': str(insight),
                            'source': source_info
                        })
                else:
                    data['insights'].append({
                        'insight': str(insights),
                        'source': source_info
                    })
            
            # Extract employee feedback
            if extracted.get('employee_feedback'):
                for feedback in extracted['employee_feedback']:
                    data['quotes'].append({
                        'quote': str(feedback),
                        'source': source_info
                    })
            
            # Extract expansion info
            if extracted.get('expansion_info'):
                for info in extracted['expansion_info']:
                    data['expansion_info'].append({
                        'info': str(info),
                        'source': source_info
                    })
        
        return data
        
    def _format_companies(self, companies: Dict[str, List]) -> str:
        """Format companies section."""
        if not companies:
            return "*No specific companies identified yet*\n"
        
        sections = []
        for company, contexts in list(companies.items())[:10]:  # Top 10 companies
            section = f"### {company}\n"
            if contexts[0]['context']:
                section += f"- Context: {contexts[0]['context']}\n"
            section += f"- Found in {len(contexts)} source(s)\n"
            section += f"- [Source: {contexts[0]['source']['title']}]({contexts[0]['source']['url']})\n"
            sections.append(section)
        
        return "\n".join(sections)
        
    def _format_challenges(self, challenges: List[Dict]) -> str:
        """Format challenges section."""
        if not challenges:
            return "*No specific challenges identified yet*\n"
        
        unique_challenges = {}
        for item in challenges:
            challenge = item['challenge']
            if challenge not in unique_challenges:
                unique_challenges[challenge] = item
        
        formatted = []
        for challenge, item in list(unique_challenges.items())[:15]:
            formatted.append(f"- {challenge} ([source]({item['source']['url']}))")
        
        return "\n".join(formatted)
        
    def _format_solutions(self, solutions: List[Dict]) -> str:
        """Format solutions section."""
        if not solutions:
            return "*No training solutions identified yet*\n"
        
        unique_solutions = {}
        for item in solutions:
            solution = item['solution']
            if solution not in unique_solutions:
                unique_solutions[solution] = item
        
        formatted = []
        for solution, item in list(unique_solutions.items())[:10]:
            formatted.append(f"- **{solution}** ([source]({item['source']['url']}))")
        
        return "\n".join(formatted)
        
    def _format_decision_makers(self, decision_makers: List[Dict]) -> str:
        """Format decision makers section."""
        if not decision_makers:
            return "*No decision makers identified yet*\n"
        
        formatted = []
        seen = set()
        
        for person in decision_makers:
            if 'name' in person and person['name'] != 'Unknown':
                key = f"{person['name']}-{person.get('company', '')}"
                if key not in seen:
                    seen.add(key)
                    formatted.append(
                        f"- **{person['name']}** - {person.get('title', 'Unknown')} "
                        f"at {person.get('company', 'Unknown')} "
                        f"([source]({person['source']['url']}))"
                    )
            elif 'info' in person:
                if person['info'] not in seen:
                    seen.add(person['info'])
                    formatted.append(f"- {person['info']} ([source]({person['source']['url']}))")
        
        return "\n".join(formatted[:10])  # Top 10
        
    def _format_key_insights(self, insights: List[Dict]) -> str:
        """Format key insights section."""
        if not insights:
            return "*No key insights extracted yet*\n"
        
        # Group similar insights and pick the best ones
        formatted = []
        seen_insights = set()
        
        for item in insights[:20]:
            insight = item['insight']
            # Simple deduplication based on first 50 chars
            insight_key = insight[:50].lower()
            if insight_key not in seen_insights:
                seen_insights.add(insight_key)
                formatted.append(
                    f"- {insight} ([source]({item['source']['url']}))"
                )
        
        return "\n".join(formatted[:10])  # Top 10 unique insights
        
    def _generate_bullet_report(self, assignment, strategy, companies_section,
                               challenges_section, solutions_section,
                               decision_makers_section, insights_section,
                               findings, structured_data):
        """Generate a bullet-point style report."""
        
        # Count unique items
        company_count = len(structured_data['companies'])
        challenge_count = len(set(item['challenge'] for item in structured_data['challenges']))
        solution_count = len(set(item['solution'] for item in structured_data['solutions']))
        decision_maker_count = len(structured_data['decision_makers'])
        
        # Get the number of cycles (it's already a number, not a list)
        num_cycles = strategy.get('cycles', 3)
        
        return f"""# {assignment['title']}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Sources Analyzed**: {len(set(f['url'] for f in findings if 'url' in f))}  
**Companies Found**: {company_count}  
**Decision Makers**: {decision_maker_count}  
**Training Solutions**: {solution_count}  

## Executive Summary

Research identified **{company_count} Japanese tech companies** with English communication needs, discovered **{challenge_count} specific challenges** they face, and found **{solution_count} training solutions** currently in use. We also identified **{decision_maker_count} potential decision makers** in HR and L&D roles.

## Research Objectives

{chr(10).join([f"- {obj}" for obj in assignment['objectives']])}

## Companies Identified

{companies_section}

## English Communication Challenges

{challenges_section}

## Current Training Solutions

{solutions_section}

## Key Decision Makers

{decision_makers_section}

## Strategic Insights

{insights_section}

## Research Methodology

{strategy['approach']}

**Search Strategy**: Conducted {num_cycles} research cycles using diverse search queries including company-specific searches, employee review platforms, industry reports, and LinkedIn profiles.

## Sources

{self._format_sources(findings)}

---
*Report generated by AI Researcher - Overnight Research Assistant*
"""
        
    def _format_sources(self, findings: List[Dict]) -> str:
        """Format unique sources as citations."""
        sources = {}
        for f in findings:
            if 'url' in f and f['url'] not in sources:
                sources[f['url']] = f.get('title', 'Untitled')
                
        formatted = []
        for i, (url, title) in enumerate(sources.items(), 1):
            formatted.append(f"{i}. [{title}]({url})")
            
        return '\n'.join(formatted[:30])  # Limit to 30 sources
        
    def _bullet_template(self) -> str:
        """Bullet point report template."""
        return "{content}"  # Now handled in _generate_bullet_report
        
    def _narrative_template(self) -> str:
        """Narrative report template."""
        return "{content}"  # Placeholder
        
    def _executive_template(self) -> str:
        """Executive summary template."""
        return "{content}"  # Placeholder
