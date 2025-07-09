#!/usr/bin/env python3
"""
Quick test script for Aria
Tests basic functionality without full research
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from aria_core.aria_personality import AriaPersonality
from aria_core.aria_voice import AriaVoice


async def test_aria():
    """Test Aria's basic functionality."""
    print("=== Testing Aria Components ===\n")
    
    # Test personality
    print("1. Testing Personality...")
    personality = AriaPersonality()
    
    print(f"Greeting: {personality.greet()}")
    
    # Test observations
    observation = personality.make_observation({
        'pattern_count': 4,
        'detail': 'Shibuya has 4 tech companies looking for English training',
        'pattern': 'geographic concentration'
    })
    print(f"Observation: {observation}")
    
    # Test response
    response = personality.respond("How's the research going?")
    print(f"Response: {response}")
    
    print("\n2. Testing Voice (if available)...")
    try:
        voice = AriaVoice(accent="irish")
        voice.test_audio()
    except Exception as e:
        print(f"Voice test skipped: {e}")
    
    print("\n3. Testing Templates...")
    from aria_core.templates import QuickTemplates
    templates = QuickTemplates()
    print("Available templates:", list(templates.templates.keys()))
    
    print("\n=== Basic Tests Complete ===")
    print("\nTo test full functionality:")
    print("  python aria.py          # Text mode")
    print("  python aria.py --voice  # Voice mode")
    print("  python aria.py --help   # See all options")


if __name__ == "__main__":
    asyncio.run(test_aria())
