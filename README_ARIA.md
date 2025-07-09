# Aria - AI Research Assistant (Development Branch)

An intelligent, conversational research assistant with voice capabilities. Built on top of the AI Researcher engine with a focus on natural interaction and helpful observations.

## What's New in Aria

- **Conversational Interface**: No more YAML files - just tell Aria what you need
- **Voice Capabilities**: 100% local voice input/output using Whisper and Piper
- **Personality & Observations**: Aria notices patterns and shares insights as she researches
- **Quick Templates**: Fast starts for common research tasks
- **Live Updates**: See progress and findings in real-time
- **Help System**: Comprehensive `/help` command with all options

## Quick Start

```bash
# Basic text mode
python aria.py

# Voice mode with Irish accent
python aria.py --voice --accent irish

# Quick competitor research
python aria.py --quick competitors

# See all options
python aria.py --help
```

## Installation

### Core Requirements (Text Mode)
```bash
# Clone the aria branch
git clone -b aria https://github.com/sean-roth/ai-researcher.git
cd ai-researcher

# Install base requirements
pip install -r requirements.txt

# Optional: Install rich for better terminal output
pip install rich
```

### Voice Mode Requirements
```bash
# Speech recognition (Whisper)
pip install openai-whisper sounddevice

# Text-to-speech (choose one)
pip install pyttsx3  # Easiest, uses system voices
# OR
pip install piper-tts  # Better quality, needs voice files
```

### Voice Setup for Piper (Optional)
```bash
# Create voices directory
mkdir voices

# Download voice files from:
# https://github.com/rhasspy/piper/releases
# 
# Recommended voices:
# - Irish/Scottish: en_GB-alba-medium.onnx
# - British: en_GB-southern_english_female-low.onnx  
# - American: en_US-amy-low.onnx
```

## Usage Examples

### Interactive Conversation
```
$ python aria.py

Aria: Morning. What are we investigating today?
You: Find me tech companies in Japan that need English training
Aria: Manufacturing, tech, or both?
You: Just tech, around 200-500 employees
Aria: I'll research Japanese tech companies with 200-500 employees that need English training. Should I start?
You: Yes

[Research Progress - 15%] ████░░░░░░░░░░░░
Aria: Found something - Sakura Tech in Tokyo just posted 5 English trainer positions...
```

### Voice Commands
```
$ python aria.py --voice

🎤 Voice mode active. Say "Hey Aria" to start.

You: "Hey Aria"
Aria: *speaks* "Yes?"
You: "Find manufacturing companies in Osaka"
Aria: *speaks* "I'll look for manufacturing companies in Osaka. Should I start?"
```

### Quick Templates
```
$ python aria.py --quick leads

Aria: Starting Lead Generation...
Aria: Describe your ideal customer (industry, size, etc.)
You: Small tech companies in need of English training
Aria: What geographic regions?
You: Japan, focusing on Tokyo and Osaka
...
```

## Commands

### During Research
- `/pause` - Pause current research
- `/resume` - Resume paused research  
- `/status` - Show current progress
- `/mute` - Toggle voice output
- `/abort` - Cancel current research
- `/focus [company]` - Focus on specific company

### General Commands
- `/help` - Show comprehensive help
- `/history` - Show recent research tasks
- `/clear` - Clear screen
- `/exit` or `/quit` - Exit Aria

## Configuration

Aria uses the same `config.yaml` as the base researcher:

```yaml
# Ollama settings
ollama:
  host: localhost
  port: 11434
  model: dolphin3:latest

# Brave Search API
brave_search:
  api_key: YOUR_API_KEY_HERE

# Research settings  
research:
  max_cycles: 5
  sources_per_cycle: 10
```

## Project Structure

```
ai-researcher/
├── aria.py              # Main Aria interface
├── aria_core/          # Aria-specific modules
│   ├── __init__.py
│   ├── aria_personality.py  # Observations & responses
│   ├── aria_voice.py       # Voice I/O (100% local)
│   └── templates.py        # Quick research templates
├── src/                # Original research engine (unchanged)
├── config.yaml         # Configuration
└── output/            # Research reports
```

## Development Status

This is the development branch for Aria. Current status:

- ✅ Conversational interface
- ✅ Personality system with observations
- ✅ Voice input/output (local)
- ✅ Quick templates
- ✅ Help system
- 🚧 Live progress updates (basic implementation)
- 🚧 Research interruption/focus commands
- 📋 Background daemon mode
- 📋 Resume from checkpoint

## Differences from Main Branch

- **Interface**: Conversational instead of YAML files
- **Entry Point**: `aria.py` instead of `run_research.py`
- **Real-time**: Live updates during research
- **Voice**: Optional voice input/output
- **Personality**: Aria makes observations about patterns

The core research engine remains unchanged - Aria is a new interface layer on top of the existing system.

## Tips

1. **Voice Quality**: For best voice output, use Piper with downloaded voice files
2. **Mute Mode**: Use `/mute` during meetings - Aria continues researching silently
3. **Quick Start**: Use `--quick` templates for common research tasks
4. **Observations**: Aria's observations can spark new research ideas
5. **History**: Check `/history` to see past research tasks

## Troubleshooting

### Voice Not Working
- Check if Whisper model downloaded: `python -c "import whisper; whisper.load_model('base')"`
- Test audio: `python aria_core/aria_voice.py`
- Ensure microphone permissions are granted

### No Audio Output
- Try pyttsx3 first: `pip install pyttsx3`
- Check system audio settings
- Run without voice: `python aria.py` (text mode)

### Research Errors
- Verify Ollama is running: `ollama serve`
- Check Brave API key in `config.yaml`
- See logs in `logs/` directory

## Contributing to Aria

When working on Aria:
1. Keep the core research engine unchanged
2. All Aria-specific code goes in `aria_core/`
3. Maintain backward compatibility with base system
4. Test both text and voice modes

## Merging to Main

When Aria is ready for main branch:
1. Extensive testing of all modes
2. Update main README with Aria option
3. Ensure `run_research.py` still works
4. Document migration path for users
