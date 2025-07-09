"""
Local voice interface for Aria using Whisper (STT) and Piper/pyttsx3 (TTS).
100% local, no cloud services required.
"""

import asyncio
import queue
import threading
import time
from pathlib import Path
from typing import Optional, Callable
import numpy as np

# Core audio handling
try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Warning: sounddevice not installed. Voice features disabled.")
    print("Install with: pip install sounddevice")

# Speech recognition (Whisper)
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: whisper not installed. Voice input disabled.")
    print("Install with: pip install openai-whisper")

# Text-to-speech options
TTS_ENGINE = None

# Try Piper first (best quality)
try:
    import piper
    TTS_ENGINE = "piper"
    print("Using Piper for text-to-speech")
except ImportError:
    # Try pyttsx3 (fallback)
    try:
        import pyttsx3
        TTS_ENGINE = "pyttsx3"
        print("Using pyttsx3 for text-to-speech")
    except ImportError:
        print("Warning: No TTS engine found. Voice output disabled.")
        print("Install with: pip install pyttsx3")


class AriaVoice:
    """Local voice interface for Aria."""
    
    def __init__(self, accent: str = "default"):
        self.accent = accent
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
        # Initialize STT (Whisper)
        self.stt_model = None
        if WHISPER_AVAILABLE and AUDIO_AVAILABLE:
            print("Loading Whisper model (this may take a moment)...")
            self.stt_model = whisper.load_model("base")  # 74MB, good balance
            print("Whisper model loaded successfully")
        
        # Initialize TTS
        self.tts_engine = None
        self._init_tts()
        
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        
    def _init_tts(self):
        """Initialize text-to-speech engine."""
        if TTS_ENGINE == "piper":
            # Piper setup
            try:
                # Map accents to Piper voices
                voice_map = {
                    'irish': 'en_GB-alba-medium.onnx',  # Scottish, close to Irish
                    'british': 'en_GB-southern_english_female-low.onnx',
                    'default': 'en_US-amy-low.onnx'
                }
                
                voice_file = voice_map.get(self.accent, voice_map['default'])
                voice_path = Path('voices') / voice_file
                
                if voice_path.exists():
                    self.tts_engine = piper.PiperVoice.load(str(voice_path))
                    print(f"Loaded Piper voice: {voice_file}")
                else:
                    print(f"Voice file not found: {voice_path}")
                    print("Download voices from: https://github.com/rhasspy/piper/releases")
                    self._fallback_to_pyttsx3()
                    
            except Exception as e:
                print(f"Piper initialization failed: {e}")
                self._fallback_to_pyttsx3()
                
        elif TTS_ENGINE == "pyttsx3":
            self._fallback_to_pyttsx3()
    
    def _fallback_to_pyttsx3(self):
        """Fallback to pyttsx3 for TTS."""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure voice
            voices = self.tts_engine.getProperty('voices')
            
            # Try to find a female voice
            female_voice_found = False
            for i, voice in enumerate(voices):
                # Common female voice indicators
                if any(indicator in voice.name.lower() for indicator in ['female', 'zira', 'hazel', 'susan', 'linda', 'karen']):
                    self.tts_engine.setProperty('voice', voice.id)
                    female_voice_found = True
                    print(f"Using voice: {voice.name}")
                    break
            
            # If no female voice found, try voice index 1 (often female on Windows)
            if not female_voice_found and len(voices) > 1:
                self.tts_engine.setProperty('voice', voices[1].id)
                print(f"Using voice: {voices[1].name}")
            
            # Try accent-specific voices
            if self.accent == 'irish' and any('irish' in v.name.lower() or 'moira' in v.name.lower() for v in voices):
                for voice in voices:
                    if 'irish' in voice.name.lower() or 'moira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            elif self.accent == 'british' and any('british' in v.name.lower() or 'uk' in v.name.lower() for v in voices):
                for voice in voices:
                    if 'british' in voice.name.lower() or 'uk' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate
            self.tts_engine.setProperty('rate', 180)
            
            print("Using pyttsx3 for text-to-speech")
            
        except Exception as e:
            print(f"pyttsx3 initialization failed: {e}")
            self.tts_engine = None
    
    def speak(self, text: str):
        """Convert text to speech and play it."""
        if not self.tts_engine:
            print(f"[No TTS] Aria would say: {text}")
            return
        
        try:
            if TTS_ENGINE == "piper" and hasattr(self.tts_engine, 'synthesize'):
                # Piper TTS
                audio_data = self.tts_engine.synthesize(text)
                if AUDIO_AVAILABLE:
                    sd.play(audio_data, samplerate=22050)
                    sd.wait()
            else:
                # pyttsx3 TTS
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
        except Exception as e:
            print(f"TTS error: {e}")
            print(f"[TTS Failed] Aria says: {text}")
    
    async def listen(self, timeout: float = 7.0) -> Optional[str]:
        """Listen for voice input and return transcribed text."""
        if not AUDIO_AVAILABLE or not self.stt_model:
            # Fallback to text input
            return input("You: ").strip()
        
        print("Listening... (speak now)")
        
        try:
            # Record audio with longer timeout
            duration = timeout
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            sd.wait()
            
            # Check if we got any significant audio
            audio_level = np.abs(recording).max()
            if audio_level < 0.002:  # Lower threshold for better detection
                print("No audio detected")
                return None
            
            # Normalize audio to improve recognition
            if audio_level < 0.1:  # Quiet audio
                recording = recording / audio_level * 0.1
            
            # Transcribe with Whisper
            print("Processing speech...")
            result = self.stt_model.transcribe(
                recording.flatten(),
                language='en',
                fp16=False,  # Use FP32 for CPU
                temperature=0.0,  # Less creative, more accurate
                suppress_tokens=[-1],  # Reduce hallucinations
                condition_on_previous_text=False  # Don't use context that might cause weird outputs
            )
            
            text = result['text'].strip()
            
            # Filter out common Whisper hallucinations
            hallucination_patterns = [
                "thank you", "thanks for watching", "subscribe",
                "sex", "xxx", "...", "bye", "goodbye"
            ]
            
            # Check if it's likely a hallucination
            if text and len(text) > 3:  # Minimum viable input
                text_lower = text.lower()
                # If the entire text is just hallucination patterns, ignore it
                if not any(pattern == text_lower for pattern in hallucination_patterns):
                    print(f"You said: {text}")
                    return text
                else:
                    print("(Filtered out likely hallucination)")
                    return None
            else:
                return None
                
        except Exception as e:
            print(f"Voice input error: {e}")
            return None
    
    async def listen_continuous(self, wake_word: str = "aria", callback: Optional[Callable] = None):
        """Continuously listen for wake word and commands."""
        if not AUDIO_AVAILABLE or not self.stt_model:
            print("Continuous listening not available without audio support")
            return
        
        print(f"Continuous listening started. Say '{wake_word}' to activate.")
        self.is_listening = True
        
        def audio_callback(indata, frames, time, status):
            """Callback for continuous audio recording."""
            if status:
                print(f"Audio error: {status}")
            self.audio_queue.put(indata.copy())
        
        # Start audio stream
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=audio_callback,
            blocksize=int(self.sample_rate * 0.5)  # 0.5 second blocks
        ):
            audio_buffer = []
            
            while self.is_listening:
                try:
                    # Get audio chunk
                    chunk = self.audio_queue.get(timeout=0.1)
                    audio_buffer.append(chunk)
                    
                    # Keep last 3 seconds
                    if len(audio_buffer) > 6:  # 6 * 0.5s = 3s
                        audio_buffer.pop(0)
                    
                    # Concatenate buffer
                    audio_data = np.concatenate(audio_buffer)
                    
                    # Quick check for speech
                    if np.abs(audio_data).max() > 0.01:
                        # Transcribe
                        result = self.stt_model.transcribe(
                            audio_data.flatten(),
                            language='en',
                            fp16=False,
                            temperature=0.0,
                            suppress_tokens=[-1],
                            condition_on_previous_text=False
                        )
                        
                        text = result['text'].strip().lower()
                        
                        # Check for wake word
                        if wake_word.lower() in text:
                            print(f"\nWake word detected!")
                            self.speak("Yes?")
                            
                            # Clear buffer and listen for command
                            audio_buffer.clear()
                            self.audio_queue.queue.clear()
                            
                            # Get the actual command
                            command = await self.listen(timeout=7.0)
                            
                            if command and callback:
                                await callback(command)
                            
                            # Resume listening
                            print(f"Listening for '{wake_word}'...")
                            
                except queue.Empty:
                    await asyncio.sleep(0.01)
                except Exception as e:
                    print(f"Continuous listening error: {e}")
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.is_listening = False
        print("Stopped listening")
    
    def test_audio(self):
        """Test audio input/output."""
        print("\n=== Audio Test ===")
        
        # Test TTS
        print("Testing text-to-speech...")
        self.speak("Hello, this is Aria. Testing voice output.")
        
        # Test STT
        if AUDIO_AVAILABLE and self.stt_model:
            print("\nTesting speech recognition...")
            print("Please say something in the next 3 seconds:")
            
            # Record
            recording = sd.rec(
                int(3 * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32
            )
            sd.wait()
            
            # Transcribe
            result = self.stt_model.transcribe(
                recording.flatten(), 
                fp16=False,
                temperature=0.0,
                suppress_tokens=[-1],
                condition_on_previous_text=False
            )
            text = result['text'].strip()
            
            if text:
                print(f"Heard: {text}")
                self.speak(f"I heard you say: {text}")
            else:
                print("No speech detected")
        else:
            print("Speech recognition not available")
        
        print("\nAudio test complete!")


# Standalone test
if __name__ == "__main__":
    print("Testing Aria Voice Module...")
    
    voice = AriaVoice(accent="irish")
    voice.test_audio()
    
    # Test continuous listening
    async def test_callback(text):
        print(f"Command received: {text}")
        voice.speak(f"You said: {text}")
    
    try:
        asyncio.run(voice.listen_continuous(callback=test_callback))
    except KeyboardInterrupt:
        print("\nTest complete!")
