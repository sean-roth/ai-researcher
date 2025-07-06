#!/usr/bin/env python3
"""Test research functionality with improvements."""

import asyncio
import argparse
import logging
import yaml
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.research_engine import ResearchEngine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_improved_research():
    """Run a test research assignment with our improvements."""
    
    # Create test assignment
    test_assignment = {
        'title': 'Japanese Tech Companies - English Training Needs Analysis',
        'priority': 'high',
        'deadline': '7:00 AM',
        'objectives': [
            'Find 10 Japanese tech companies that have recently expanded globally',
            'Identify English communication challenges mentioned in employee reviews',
            'Discover what English training solutions they currently use',
            'Find decision makers in HR or Training departments'
        ],
        'depth': 'comprehensive',
        'report_style': 'bullets',
        'output': {
            'format': 'single',
            'max_reports': 1
        }
    }
    
    # Save test assignment
    assignment_path = Path('test_assignment_improved.yaml')
    with open(assignment_path, 'w') as f:
        yaml.dump(test_assignment, f)
    
    print(f"Created test assignment: {assignment_path}")
    
    # Run research
    try:
        engine = ResearchEngine('config.yaml')
        print("\nStarting research engine...")
        print("This will take several minutes as it performs multiple search cycles.")
        print("Watch the logs to see the improved search queries and extraction in action.\n")
        
        reports = await engine.process_assignment(assignment_path)
        
        print(f"\nResearch complete! Generated {len(reports)} report(s):")
        for report in reports:
            print(f"  - {report}")
            
        # Display a preview of the report
        if reports:
            print(f"\n{'='*60}")
            print("REPORT PREVIEW (first 2000 chars):")
            print('='*60)
            with open(reports[0], 'r') as f:
                content = f.read()
                print(content[:2000])
                if len(content) > 2000:
                    print(f"\n... (truncated - full report is {len(content)} chars)")
            
    except Exception as e:
        logging.error(f"Test failed: {e}", exc_info=True)
        return False
    
    return True

async def quick_test_extraction():
    """Quick test of just the extraction capabilities."""
    from src.web_researcher import WebResearcher
    
    print("Testing improved extraction on a single URL...")
    
    researcher = WebResearcher('config.yaml')
    
    # Test with a specific query
    findings = await researcher.search_and_analyze(
        "Japanese tech companies English training programs",
        ['corporate sites', 'news', 'industry reports']
    )
    
    print(f"\nFound {len(findings)} relevant sources")
    
    for i, finding in enumerate(findings, 1):
        print(f"\n{'='*60}")
        print(f"Finding {i}: {finding.get('title', 'Unknown')}")
        print(f"URL: {finding.get('url', 'Unknown')}")
        print(f"Quality Score: {finding.get('quality_score', 0)}/10")
        
        if 'extracted_data' in finding:
            data = finding['extracted_data']
            print("\nExtracted Data:")
            
            if data.get('companies'):
                print(f"  Companies: {data['companies'][:3]}")  # First 3
            
            if data.get('english_challenges'):
                print(f"  Challenges: {data['english_challenges'][:2]}")  # First 2
                
            if data.get('current_solutions'):
                print(f"  Solutions: {data['current_solutions'][:2]}")  # First 2
                
            if data.get('decision_makers'):
                print(f"  Decision Makers: {data['decision_makers'][:2]}")  # First 2

def main():
    parser = argparse.ArgumentParser(description='Test improved AI Researcher')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick extraction test instead of full research')
    parser.add_argument('--config', default='config.yaml',
                       help='Path to config file')
    
    args = parser.parse_args()
    
    # Check if config exists
    if not Path(args.config).exists():
        print(f"Error: Config file '{args.config}' not found.")
        print("Please copy config.example.yaml to config.yaml and add your Brave API key.")
        return
    
    # Run the appropriate test
    if args.quick:
        asyncio.run(quick_test_extraction())
    else:
        success = asyncio.run(test_improved_research())
        if success:
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Test failed - check logs for details")

if __name__ == "__main__":
    main()
