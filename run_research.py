#!/usr/bin/env python3
"""Run the AI Researcher with proper logging setup."""

import asyncio
import logging
from pathlib import Path
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.research_engine import ResearchEngine

def setup_logging():
    """Set up logging to both console and file."""
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Log filename with timestamp
    log_file = log_dir / f"research_{datetime.now():%Y%m%d_%H%M%S}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler - saves everything to file
            logging.FileHandler(log_file),
            # Console handler - shows INFO and above
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from some libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    print(f"\n📝 Logs will be saved to: {log_file}")
    return log_file

async def main():
    """Run the research with the test assignment."""
    # Set up logging
    log_file = setup_logging()
    
    # Use the test assignment
    assignment_path = Path('test_assignment_improved.yaml')
    
    if not assignment_path.exists():
        print(f"❌ Assignment file not found: {assignment_path}")
        print("Run 'python tests/test_improved_research.py' first to create it.")
        return
    
    print("\n🚀 Starting AI Researcher...")
    print("This will take 10-20 minutes to complete.")
    print("Watch the progress here or check the log file.\n")
    
    try:
        engine = ResearchEngine('config.yaml')
        reports = await engine.process_assignment(assignment_path)
        
        print(f"\n✅ Research complete! Generated {len(reports)} report(s):")
        for report in reports:
            print(f"  📄 {report}")
            
        # Show a preview
        if reports:
            print(f"\n{'='*60}")
            print("REPORT PREVIEW (first 1000 chars):")
            print('='*60)
            with open(reports[0], 'r') as f:
                content = f.read()
                print(content[:1000])
                if len(content) > 1000:
                    print(f"\n... (full report is {len(content)} chars)")
            
            print(f"\n📄 Full report saved to: {reports[0]}")
            
    except Exception as e:
        logging.error(f"Research failed: {e}", exc_info=True)
        print(f"\n❌ Research failed: {e}")
        print(f"Check the log file for details: {log_file}")
        return
    
    print(f"\n📝 Complete logs saved to: {log_file}")
    print("💡 Tip: Use 'tail -f {log_file}' to watch logs in real-time")

if __name__ == "__main__":
    asyncio.run(main())
