#!/usr/bin/env python3
"""Test extraction with sample content to verify LLM is working correctly."""

import asyncio
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.web_researcher import WebResearcher

# Sample content that should definitely extract data
SAMPLE_CONTENTS = [
    {
        'name': 'Rakuten Article',
        'content': """
        Rakuten's English Initiative: A Decade Later
        
        Rakuten, Japan's largest e-commerce company, made headlines in 2010 when CEO Hiroshi Mikitani 
        announced that English would become the company's official language. This bold move, dubbed 
        "Englishnization," was part of Rakuten's strategy to become a global internet services company.
        
        The Challenge:
        Many Japanese engineers struggled with the transition. "At first, our meeting productivity 
        dropped by 30-40%," says Takashi Yamamoto, Senior VP of Engineering. "Engineers could not 
        express complex technical concepts in English, and code reviews took three times longer."
        
        The Solution:
        Rakuten invested heavily in English training:
        - Partnered with Berlitz for on-site corporate training
        - Required all employees to achieve TOEIC score of 700+
        - Provided 2 hours per week of paid study time
        - Created internal English conversation clubs
        
        The investment was substantial - approximately $5 million per year on language training alone.
        
        Results:
        By 2024, Rakuten has successfully expanded globally with offices in the US, Europe, and Asia.
        The company credits its English policy for enabling smoother integration of international 
        acquisitions and attracting global talent.
        
        HR Director Yuki Sato notes: "While challenging, the English initiative has been crucial for 
        our global expansion. We continue to refine our training programs based on employee feedback."
        """
    },
    {
        'name': 'Job Listings Page',
        'content': """
        Tech Jobs in Japan - Current Openings
        
        Software Engineer - Mercari
        Location: Tokyo
        Requirements: Business-level English required for global team collaboration
        
        Senior Developer - LINE Corporation  
        Location: Tokyo/Remote
        Note: Daily standup meetings conducted in English
        
        Backend Engineer - SmartNews
        Location: Tokyo
        Language: English required, Japanese nice to have
        
        Machine Learning Engineer - Preferred Networks
        Location: Tokyo
        Requirements: English documentation skills essential
        """
    },
    {
        'name': 'Employee Review',
        'content': """
        Working at CyberAgent - Employee Review
        
        Pros:
        - Great technical team and interesting projects
        - Good work-life balance
        
        Cons:
        - English communication is a major challenge
        - International meetings are difficult when you can't express ideas clearly
        - Company provides English lessons but they're too general, not tech-focused
        - Need more practical English training for engineers
        
        The company is trying to expand globally but the language barrier is real. They recently 
        started using Rosetta Stone for employees but it's not enough for technical discussions.
        """
    }
]

async def test_extraction():
    """Test the extraction on known good content."""
    
    researcher = WebResearcher('config.yaml')
    
    print("="*60)
    print("TESTING EXTRACTION WITH SAMPLE CONTENT")
    print("="*60)
    
    for sample in SAMPLE_CONTENTS:
        print(f"\n\nTesting: {sample['name']}")
        print("-"*40)
        
        # Test extraction
        extracted = await researcher.extract_structured_data(
            sample['content'],
            "Japanese tech companies English training",
            "test://sample"
        )
        
        print("\nExtracted Data:")
        print(json.dumps(extracted, indent=2))
        
        # Summary
        print(f"\nSummary:")
        print(f"  Companies: {len(extracted.get('companies', []))}")
        print(f"  Challenges: {len(extracted.get('english_challenges', []))}")
        print(f"  Solutions: {len(extracted.get('current_solutions', []))}")
        print(f"  Decision Makers: {len(extracted.get('decision_makers', []))}")
        print(f"  Relevant: {extracted.get('relevant_findings', False)}")
        
        if not extracted.get('relevant_findings'):
            print("\n⚠️  WARNING: Extraction failed on sample content!")
            print("This suggests the LLM prompt needs adjustment.")

async def test_brave_search():
    """Test the new direct Brave Search implementation."""
    
    researcher = WebResearcher('config.yaml')
    
    if researcher.brave_api_key:
        print("\n\n" + "="*60)
        print("TESTING BRAVE SEARCH")
        print("="*60)
        
        query = "Japanese tech companies English training"
        print(f"\nSearching for: {query}")
        
        urls = await researcher.search_brave_direct(query, count=5)
        
        print(f"\nFound {len(urls)} results:")
        for i, url_info in enumerate(urls, 1):
            print(f"\n{i}. {url_info['title']}")
            print(f"   URL: {url_info['url']}")
            print(f"   Description: {url_info['description'][:100]}...")
    else:
        print("\n⚠️  Brave Search not configured")

async def test_full_pipeline():
    """Test the complete search and analyze pipeline."""
    
    researcher = WebResearcher('config.yaml')
    
    print("\n\n" + "="*60)
    print("TESTING FULL PIPELINE")
    print("="*60)
    
    query = "Rakuten English training corporate language"
    print(f"\nSearching and analyzing: {query}")
    
    findings = await researcher.search_and_analyze(
        query,
        ['corporate sites', 'news', 'employee reviews']
    )
    
    print(f"\nFound {len(findings)} relevant sources")
    
    for i, finding in enumerate(findings, 1):
        print(f"\n{i}. {finding['title']}")
        print(f"   URL: {finding['url']}")
        print(f"   Quality: {finding['quality_score']}/10")
        
        data = finding.get('extracted_data', {})
        if data.get('companies'):
            print(f"   Companies: {data['companies'][:2]}")
        if data.get('english_challenges'):
            print(f"   Challenges: {data['english_challenges'][:1]}")

async def main():
    """Run all tests."""
    # First test extraction on known content
    await test_extraction()
    
    # Then test Brave Search
    await test_brave_search()
    
    # Finally test full pipeline
    await test_full_pipeline()

if __name__ == "__main__":
    asyncio.run(main())
