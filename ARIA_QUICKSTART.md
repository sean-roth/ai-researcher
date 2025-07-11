# Aria Quick Start Guide

## Morning Lead Generation Workflow

### 1. Start Aria with Voice
```bash
python aria.py --voice
```

### 2. Request Lead Generation
Say or type:
```
"Find 40 manufacturing companies in Japan that need English training"
```

Aria will ask clarifying questions:
- Company size? → "200 to 500 employees"
- What info do you need? → "Challenges and contacts"
- How many? → "Forty"

### 3. Let Aria Work
- Research will take 20-40 minutes for 40 leads
- You'll see progress updates and observations
- Reports save to `output/` directory

### 4. Review Results
The report will have:
- **Hot Leads**: Companies with urgent needs + decision makers
- **Warm Leads**: Clear needs, some info missing
- **Cold Leads**: Potential needs, need more research

## Afternoon Course Creation

### 1. New Research Task
```
"Research content for an English email course for Japanese engineers"
```

### 2. Monitor Progress
- Keep laptop on side table with USB mic
- Use mute button between commands
- Say "status" to check progress
- Observations help refine the search

## Tips for Success

### Voice Mode
- Speak naturally, the 7-second timeout allows pauses
- Use the mute button on your USB mic when not speaking
- Say "exit" or "/exit" to quit

### Research Quality
- Be specific: "tech companies" → "software companies"
- Include location: Always specify city/country
- Set clear limits: "20 companies" not "some companies"

### Working Together
1. **Aria finds leads** (morning)
2. **We verify and personalize** (work together during day)
3. **Aria researches courses** (afternoon while you work)

## Common Commands

During research:
- "Hey Aria, status?" - Check progress
- "Hey Aria, pause" - Pause research
- "Hey Aria, focus on Tokyo companies" - Refine search

General:
- "/help" - Show all commands
- "/history" - See past research
- "/mute" - Toggle voice output

## Prompt Library

Aria uses structured prompts for each task:
- `prompts/research/lead_generation.md` - For finding companies
- `prompts/special/course_creation.md` - For course content
- Add your own in `prompts/` as you discover edge cases

## Example Daily Routine

**7:00 AM**: Start Aria for lead generation
**7:30 AM**: Review overnight research, start new batch
**9:00 AM**: Work with me to verify leads and send messages
**2:00 PM**: Set Aria to research course content
**5:00 PM**: Review course research findings

## Troubleshooting

**Voice not working?**
- Check mic is default in Windows settings
- Run `python test_voices.py` to test
- Ensure earbuds/USB mic is connected

**Research going off track?**
- Check the prompt in `prompts/` directory
- Make it more specific
- Add constraints to prevent drift

**Too many/few results?**
- Adjust the number in your request
- "Find exactly 20 companies" for precision
