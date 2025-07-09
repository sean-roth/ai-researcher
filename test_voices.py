#!/usr/bin/env python3
"""
Voice Setup Test for Aria
Helps troubleshoot and configure voice settings
"""

import pyttsx3
import time


def test_voices():
    """List all available voices and test them."""
    print("=== Testing Available Voices ===\n")
    
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    print(f"Found {len(voices)} voices:\n")
    
    for i, voice in enumerate(voices):
        print(f"Voice {i}:")
        print(f"  Name: {voice.name}")
        print(f"  ID: {voice.id}")
        print(f"  Gender: {voice.gender if hasattr(voice, 'gender') else 'Unknown'}")
        print(f"  Languages: {voice.languages if hasattr(voice, 'languages') else 'Unknown'}")
        
        # Test the voice
        engine.setProperty('voice', voice.id)
        engine.setProperty('rate', 180)
        
        # Determine if it's likely female based on common indicators
        is_female = any(indicator in voice.name.lower() for indicator in 
                       ['female', 'zira', 'hazel', 'susan', 'linda', 'karen', 'samantha', 'victoria'])
        
        if is_female:
            print("  ** Likely FEMALE voice **")
        
        engine.say(f"This is voice number {i}. Hello, I'm Aria, your research assistant.")
        engine.runAndWait()
        
        print()
        time.sleep(0.5)
    
    print("\n=== Recommendation ===")
    print("To use a specific voice, note the number and update aria_core/aria_voice.py")
    print("In the _fallback_to_pyttsx3() method, add:")
    print("  self.tts_engine.setProperty('voice', voices[X].id)  # Replace X with voice number")
    
    # Try to recommend a female voice
    female_indices = []
    for i, voice in enumerate(voices):
        if any(indicator in voice.name.lower() for indicator in 
               ['female', 'zira', 'hazel', 'susan', 'linda', 'karen', 'samantha', 'victoria']):
            female_indices.append(i)
    
    if female_indices:
        print(f"\nDetected likely female voices at indices: {female_indices}")
        print(f"Recommended: Use voice {female_indices[0]}")


if __name__ == "__main__":
    test_voices()
