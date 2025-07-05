"""Report generation for research findings."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

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
        template = self.templates.get(style, self.templates['bullets'])
        
        # Format findings
        formatted_findings = self._format_findings(findings, style)
        
        # Generate report content
        report_content = template.format(
            title=assignment['title'],
            date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            objectives='\n'.join([f"- {obj}" for obj in assignment['objectives']]),
            strategy=strategy['approach'],
            findings=formatted_findings,
            sources=self._format_sources(findings),
            total_sources=len(set(f['url'] for f in findings if 'url' in f))
        )
        
        # Save report
        report_path = Path('output') / f"{assignment['title'][:50]}_{datetime.now():%Y%m%d_%H%M}.md"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report_content)
        
        logger.info(f"Report generated: {report_path}")
        return report_path
        
    async def _generate_focused_report(self, assignment: Dict, findings: List[Dict],
                                     focus: str, style: str) -> Path:
        """Generate a focused report on a specific aspect."""
        # Similar to single report but with focused title and content
        template = self.templates.get(style, self.templates['bullets'])
        
        report_content = template.format(
            title=f"{assignment['title']} - {focus}",
            date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            objectives=f"Focus: {focus}",
            strategy="Targeted research",
            findings=self._format_findings(findings, style),
            sources=self._format_sources(findings),
            total_sources=len(set(f['url'] for f in findings if 'url' in f))
        )
        
        report_path = Path('output') / f"{focus}_{datetime.now():%Y%m%d_%H%M}.md"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report_content)
        
        return report_path
        
    def _format_findings(self, findings: List[Dict], style: str) -> str:
        """Format findings based on report style."""
        if style == 'bullets':
            formatted = []
            for f in findings[:20]:  # Limit to top 20
                formatted.append(
                    f"- **{f.get('title', 'Finding')}**: {f.get('key_insight', 'No insight')}\n"
                    f"  - Source: [{f.get('url', 'Unknown')}]({f.get('url', '#')})\n"
                    f"  - Quality: {f.get('quality_score', 0)}/10\n"
                )
            return '\n'.join(formatted)
            
        elif style == 'narrative':
            # Create a flowing narrative from findings
            insights = [f.get('key_insight', '') for f in findings if f.get('key_insight')]
            return ' '.join(insights[:10])
            
        else:  # executive
            # High-level summary
            return self._create_executive_summary(findings)
            
    def _format_sources(self, findings: List[Dict]) -> str:
        """Format unique sources as citations."""
        sources = {}
        for f in findings:
            if 'url' in f and f['url'] not in sources:
                sources[f['url']] = f.get('title', 'Untitled')
                
        formatted = []
        for i, (url, title) in enumerate(sources.items(), 1):
            formatted.append(f"{i}. [{title}]({url})")
            
        return '\n'.join(formatted[:20])  # Limit to 20 sources
        
    def _group_findings(self, findings: List[Dict], assignment: Dict) -> Dict[str, List[Dict]]:
        """Group findings by theme or objective."""
        groups = {}
        
        # Simple grouping by objective keywords
        for obj in assignment['objectives']:
            obj_key = obj[:30]  # Short key
            groups[obj_key] = [
                f for f in findings 
                if any(word in f.get('key_insight', '').lower() 
                      for word in obj.lower().split())
            ]
            
        return groups
        
    def _create_executive_summary(self, findings: List[Dict]) -> str:
        """Create executive summary from findings."""
        summary_parts = [
            "## Key Discoveries\n",
            f"Analyzed {len(findings)} sources with the following insights:\n"
        ]
        
        # Top 5 insights
        top_findings = sorted(findings, key=lambda x: x.get('quality_score', 0), reverse=True)[:5]
        
        for i, f in enumerate(top_findings, 1):
            summary_parts.append(
                f"{i}. {f.get('key_insight', 'No insight available')[:200]}...\n"
            )
            
        return '\n'.join(summary_parts)
        
    def _bullet_template(self) -> str:
        """Bullet point report template."""
        return """# {title}

**Generated**: {date}  
**Total Sources Analyzed**: {total_sources}

## Objectives
{objectives}

## Research Strategy
{strategy}

## Key Findings

{findings}

## Sources

{sources}

---
*Report generated by AI Researcher*
"""
        
    def _narrative_template(self) -> str:
        """Narrative report template."""
        return """# {title}

**Date**: {date}

## Executive Summary

Based on analysis of {total_sources} sources, our research reveals:

{findings}

## Research Objectives
{objectives}

## Methodology
{strategy}

## References
{sources}
"""
        
    def _executive_template(self) -> str:
        """Executive summary template."""
        return """# {title} - Executive Brief

**Date**: {date}  
**Sources**: {total_sources}

{findings}

## Next Steps
Based on these findings, recommended actions include further investigation into the most promising opportunities identified above.

## Full Source List
{sources}
"""