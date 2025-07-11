# Aria Prompt Library

This directory contains structured prompts for different research tasks. These prompts help keep the 8B Dolphin model focused and prevent it from going off-track.

## Structure

```
prompts/
├── research/          # Core research prompts
│   ├── lead_generation.md
│   ├── competitor_analysis.md
│   ├── grant_research.md
│   └── market_analysis.md
├── extraction/        # Data extraction prompts
│   ├── company_details.md
│   ├── contact_finder.md
│   └── needs_analysis.md
├── strategy/          # Research strategy prompts
│   ├── search_planning.md
│   └── source_evaluation.md
└── special/          # Special purpose prompts
    ├── course_creation.md
    └── idea_validation.md
```

## Usage

Aria loads these prompts based on the research task. They provide:
- Clear objectives
- Specific output formats
- Examples of good responses
- Constraints to prevent drift

## Adding New Prompts

When you encounter new edge cases:
1. Create a new `.md` file in the appropriate directory
2. Use the template structure (see existing prompts)
3. Test with a small research task first
4. Refine based on results
