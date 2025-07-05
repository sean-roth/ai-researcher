# AI Researcher - Overnight Research Assistant

An autonomous AI research assistant that runs on a spare GPU laptop (RTX 3060, 6GB VRAM) to perform deep research while you sleep. Built with Dolphin-Llama3 8B for uncensored analysis and designed for single-agent, methodical research.

## Project Philosophy

Unlike multi-agent systems optimized for speed, this researcher optimizes for depth and quality:
- **Time is abundant**: 8-hour overnight runs allow thorough research
- **Hardware is limited**: Single agent architecture for 6GB VRAM constraint  
- **Quality over quantity**: Deep understanding of 20 companies beats surface scanning 100
- **Crash resilient**: Checkpoints progress throughout the night
- **Zero cloud dependency**: Runs entirely on local hardware

## Quick Start

```bash
# Clone the repository
git clone https://github.com/sean-roth/ai-researcher.git
cd ai-researcher

# Install dependencies
pip install -r requirements.txt

# Configure LocalSend paths
cp config.example.yaml config.yaml
# Edit config.yaml with your paths

# Test single company research
python test_research.py --company "Rakuten" --max-time 30
```

## Architecture Overview

```
Main Computer                    GPU Laptop (Windows)
─────────────                   ─────────────────────
│ Create Assignment │           │ Docker Container   │
│ Drop in LocalSend │ ────────► │ - Dolphin 8B LLM   │
│ Go to sleep       │           │ - Crawl4ai         │
│                   │ ◄──────── │ - Research Engine  │
│ Morning: Reports  │           │ - Report Generator │
└───────────────────┘           └────────────────────┘
```

## Features

### Current (MVP)
- Monitor LocalSend folder for research assignments
- Develop research strategies using AI
- Execute multi-cycle web research with source evaluation
- Generate markdown reports with citations
- Checkpoint progress for crash recovery
- Basic thermal monitoring

### Planned
- Lead enrichment specialization for B2B sales
- API integrations (Reddit, SEC, job boards)
- Multiple report formats (executive, detailed, bullets)
- Research memory system for cumulative learning
- Web UI for assignment creation
- Email integration for urgent findings

## Project Structure

```
ai-researcher/
├── src/
│   ├── research_engine.py    # Core research orchestration
│   ├── web_researcher.py     # Crawl4ai integration
│   ├── report_writer.py      # Report generation
│   ├── file_monitor.py       # LocalSend integration
│   └── thermal_monitor.py    # Hardware monitoring
├── prompts/
│   ├── research_strategy.txt # Strategy development
│   ├── source_evaluation.txt # Quality assessment
│   └── report_templates/     # Various formats
├── config/
│   ├── config.example.yaml   # Configuration template
│   └── sources.yaml          # Trusted sources list
├── tests/
│   ├── test_minimal.py       # Basic connectivity test
│   └── test_research.py      # Full research test
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
└── examples/
    └── assignments/          # Example research requests
```

## Research Flow

1. **Assignment Detection**: Monitor LocalSend folder for new `.yaml` assignments
2. **Strategy Development**: AI analyzes assignment and creates research plan
3. **Research Cycles**:
   - Generate diverse search queries
   - Evaluate source quality
   - Extract relevant information
   - Refine strategy based on findings
4. **Report Generation**: Create structured markdown reports
5. **Delivery**: Save reports to LocalSend output folder

## Assignment Format

```yaml
# research_assignment.yaml
title: "English Training Market Analysis - Japanese Tech Companies"
priority: high
deadline: "7:00 AM"

objectives:
  - Find 20 Japanese tech companies struggling with English
  - Identify decision makers and budget cycles
  - Discover competitor weaknesses

depth: comprehensive  # or "quick_scan"
report_style: bullets  # or "narrative" or "executive"

special_sources:
  - Reddit discussions about workplace English
  - Job boards with English requirements
  - Recent press releases about expansion

output:
  format: multiple  # or "single"
  max_reports: 5
```

## Development Roadmap

### Phase 1: Core Engine (Current)
- [x] Repository setup
- [ ] Basic research loop
- [ ] Crawl4ai integration  
- [ ] Ollama/Dolphin connection
- [ ] LocalSend file monitoring
- [ ] Simple report generation
- [ ] Thermal monitoring

### Phase 2: Research Quality
- [ ] Source evaluation system
- [ ] Research strategy planning
- [ ] Multi-cycle refinement
- [ ] Checkpoint/resume system
- [ ] Citation management

### Phase 3: Specialization
- [ ] Lead enrichment module
- [ ] Job search module
- [ ] Market intelligence module
- [ ] API integrations

### Phase 4: Scale
- [ ] Docker containerization
- [ ] Web interface
- [ ] Multi-GPU support
- [ ] Cloud deployment option

## Hardware Requirements

- **GPU**: NVIDIA RTX 3060 or better (6GB+ VRAM)
- **RAM**: 16GB minimum
- **Storage**: 50GB for models and data
- **OS**: Windows 10/11 with WSL2 or Linux
- **Network**: Stable internet for web research

## Dependencies

- Python 3.10+
- Ollama (for running Dolphin-Llama3)
- Docker (optional, for containerization)
- LocalSend (for file transfer between computers)

## Contributing

This project is designed to be hackable and extensible. Key areas for contribution:
- New research modules
- Additional API integrations
- Improved prompts
- Report format templates
- Hardware optimization

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Dolphin-Llama3 by Eric Hartford for uncensored analysis
- Crawl4ai for intelligent web scraping
- LocalSend for secure local file transfer
- Anthropic's research on multi-agent systems for architectural insights
