# Aria Update: Prompt Library & Workflow Enhancements

## What's New

### 1. **Prompt Library System**
- Structured prompts in `prompts/` directory keep the 8B model focused
- Organized by type: research, extraction, special purposes
- Easy to add new prompts as you discover edge cases

### 2. **Enhanced Workflow Support**
- **Morning**: Lead generation (40-50 companies)
- **Day**: Work with Claude to verify and personalize
- **Afternoon**: Course creation research while you work

### 3. **Voice Improvements**
- Longer timeouts (7 seconds) for natural speech pauses
- Better female voice selection
- Whisper hallucination filtering
- Natural language number parsing ("just one" → 1)

### 4. **USB Mic Ready**
- Optimized for your gooseneck USB mic
- Physical mute button support
- Better audio detection thresholds

## Key Files Added/Updated

### New Prompts
- `prompts/research/lead_generation.md` - Find companies needing English training
- `prompts/special/course_creation.md` - Research course content
- `prompts/extraction/company_details.md` - Extract company info accurately

### System Updates
- `aria_core/prompt_library.py` - Manages all prompts
- `aria_core/research_integration.py` - Uses prompts automatically
- `aria_core/templates.py` - Handles natural language numbers
- `aria_core/aria_voice.py` - Better voice handling

### Documentation
- `ARIA_QUICKSTART.md` - Your daily workflow guide
- `prompts/README.md` - How to add new prompts

## Your Daily Workflow

```bash
# Morning (7:00 AM)
python aria.py --voice
"Find 40 manufacturing companies in Japan that need English training"

# Work with Claude (9:00 AM)
# Verify leads and craft personalized messages together

# Afternoon (2:00 PM)
"Research content for an English email course for engineers"

# Monitor from your desk with USB mic
# Use mute button between commands
# Observations help refine the search
```

## Quick Tips

1. **Be Specific**: The prompts guide Aria to find exactly what you need
2. **Use the Mic**: Physical mute button = clear start/stop for commands
3. **Add Edge Cases**: Save new prompts when you find gaps
4. **Trust the Process**: 8B model + good prompts = focused results

The system is ready for your workflow. When your USB mic arrives, you'll have a powerful research assistant that finds leads while you sleep and creates courses while you work!
