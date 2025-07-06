#!/usr/bin/env python3
"""Minimal example showing what the output should look like."""

import asyncio
from pathlib import Path
import json
from datetime import datetime

async def create_example_output():
    """Create an example of what the research output should look like."""
    
    # Example of what the system should find
    example_findings = [
        {
            'url': 'https://www.example.com/rakuten-english',
            'title': 'Rakuten Global Expansion and English Challenges',
            'quality_score': 9,
            'extracted_data': {
                'companies': [
                    {'name': 'Rakuten', 'context': 'Made English official language in 2010, expanded to US in 2024'},
                    {'name': 'Mercari', 'context': 'Japanese e-commerce expanding to US market'}
                ],
                'english_challenges': [
                    'Engineers struggle with technical documentation in English',
                    'Meeting participation drops 40% when conducted in English',
                    'Email communication takes 3x longer for non-native speakers'
                ],
                'current_solutions': [
                    'Berlitz corporate training program - 2 hours/week',
                    'TOEIC score requirements (minimum 700)',
                    'English-only meeting days'
                ],
                'decision_makers': [
                    {'name': 'Hiroshi Tanaka', 'title': 'VP of Global Talent', 'company': 'Rakuten'},
                    {'name': 'Yuki Sato', 'title': 'L&D Manager', 'company': 'Mercari'}
                ],
                'key_insights': [
                    'Companies spending average $2M/year on English training',
                    'ROI unclear - only 30% of employees show improvement',
                    'Need for more practical, tech-focused English training'
                ],
                'relevant_findings': True
            }
        },
        {
            'url': 'https://www.example.com/glassdoor-reviews',
            'title': 'Employee Reviews - Japanese Tech Companies',
            'quality_score': 8,
            'extracted_data': {
                'companies': [
                    {'name': 'LINE', 'context': 'Messaging app company with offices in Korea and Japan'}
                ],
                'english_challenges': [
                    '"Daily standup in English is painful" - Senior Developer',
                    '"Can\'t express technical concepts clearly" - Team Lead'
                ],
                'employee_feedback': [
                    'Company provides English lessons but they\'re too general',
                    'Need more technical vocabulary training'
                ],
                'relevant_findings': True
            }
        }
    ]
    
    # Create example report
    print("=" * 60)
    print("EXAMPLE: What the AI Researcher Should Produce")
    print("=" * 60)
    
    print("\n## Executive Summary\n")
    print("Research identified 3 Japanese tech companies with English communication needs:")
    print("- Rakuten (official English policy since 2010)")
    print("- Mercari (expanding to US market)")  
    print("- LINE (international offices)")
    
    print("\n## Key Findings\n")
    
    print("\n### Companies & Their Challenges")
    for finding in example_findings:
        data = finding['extracted_data']
        if data.get('companies'):
            for company in data['companies']:
                print(f"\n**{company['name']}**")
                print(f"- Context: {company['context']}")
                if data.get('english_challenges'):
                    print("- Challenges:")
                    for challenge in data['english_challenges'][:2]:
                        print(f"  • {challenge}")
    
    print("\n### Current Training Solutions")
    solutions = set()
    for finding in example_findings:
        for solution in finding['extracted_data'].get('current_solutions', []):
            solutions.add(solution)
    for solution in solutions:
        print(f"- {solution}")
    
    print("\n### Decision Makers")
    for finding in example_findings:
        for person in finding['extracted_data'].get('decision_makers', []):
            print(f"- {person['name']} - {person['title']} at {person['company']}")
    
    print("\n### Strategic Insights")
    for finding in example_findings:
        for insight in finding['extracted_data'].get('key_insights', [])[:2]:
            print(f"- {insight}")
    
    # Save example data
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    example_file = output_dir / 'example_extracted_data.json'
    with open(example_file, 'w') as f:
        json.dump(example_findings, f, indent=2)
    
    print(f"\n\n✅ Example data saved to: {example_file}")
    print("\nThis is what your extraction should look like!")
    print("Compare this with what you're actually getting.\n")

if __name__ == "__main__":
    asyncio.run(create_example_output())
