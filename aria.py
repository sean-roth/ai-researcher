#!/usr/bin/env python3
"""
Aria - Your AI Research Assistant
A conversational interface for the AI Researcher with voice capabilities.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.research_engine import ResearchEngine
from aria_core.aria_personality import AriaPersonality
from aria_core.aria_voice import AriaVoice
from aria_core.templates import QuickTemplates
from aria_core.research_integration import AriaResearchIntegration

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Note: Install 'rich' for better terminal output: pip install rich")

console = Console() if RICH_AVAILABLE else None


class Aria:
    """Main Aria assistant class."""
    
    def __init__(self, voice_enabled=False, voice_accent="default", hybrid_mode=False):
        self.personality = AriaPersonality()
        self.templates = QuickTemplates()
        self.research_integration = AriaResearchIntegration('config.yaml')
        
        # Voice setup
        self.voice_enabled = voice_enabled
        self.hybrid_mode = hybrid_mode
        self.voice = None
        if voice_enabled:
            try:
                self.voice = AriaVoice(accent=voice_accent)
                self.output("Voice mode initialized. Say 'Hey Aria' to start.", style="info")
            except Exception as e:
                self.output(f"Voice initialization failed: {e}", style="error")
                self.voice_enabled = False
        
        # State
        self.is_researching = False
        self.muted = False
        self.research_history = self._load_history()
        
    def output(self, text: str, style: str = "default", speak: bool = True):
        """Output text with optional voice."""
        # Console output
        if console and style != "default":
            if style == "info":
                console.print(f"[blue]ℹ {text}[/blue]")
            elif style == "success":
                console.print(f"[green]✓ {text}[/green]")
            elif style == "error":
                console.print(f"[red]✗ {text}[/red]")
            elif style == "aria":
                console.print(f"[cyan]Aria:[/cyan] {text}")
            elif style == "observation":
                console.print(f"[yellow]💡 Aria:[/yellow] [italic]{text}[/italic]")
            else:
                console.print(text)
        else:
            if style == "aria":
                print(f"Aria: {text}")
            elif style == "observation":
                print(f"💡 Aria: {text}")
            else:
                print(text)
        
        # Voice output
        if self.voice_enabled and speak and not self.muted and self.voice:
            if style in ["aria", "observation"] or (self.hybrid_mode and style in ["info", "success"]):
                self.voice.speak(text)
    
    def show_help(self):
        """Display help information."""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    ARIA - AI Research Assistant               ║
╚══════════════════════════════════════════════════════════════╝

USAGE: python aria.py [options]

OPTIONS:
  --voice              Enable voice input/output
  --accent ACCENT      Voice accent (irish, british, default)
  --hybrid             Voice input with text + voice output
  --quick TASK         Quick research with predefined template
  --resume             Resume from last checkpoint
  --daemon             Run in background, notify on findings
  --mute               Start with voice muted
  --help, -h           Show this help message

INTERACTIVE COMMANDS:
  During research:
    /pause           Pause current research
    /resume          Resume paused research
    /status          Show current progress
    /mute            Toggle voice output
    /abort           Cancel current research
    /focus COMPANY   Focus on specific company
    
  General:
    /help            Show this help
    /history         Show recent research tasks
    /clear           Clear screen
    /exit, /quit     Exit Aria

QUICK START EXAMPLES:
  # Text mode
  $ python aria.py
  
  # Voice mode with Irish accent
  $ python aria.py --voice --accent irish
  
  # Quick competitor research
  $ python aria.py --quick competitors
  
  # Resume last research
  $ python aria.py --resume

RESEARCH TEMPLATES:
  competitors     Find competitor companies
  leads          Generate sales leads
  grants         Find relevant grants
  ideas          Validate business ideas
  people         Find decision makers
  market         Market analysis

VOICE COMMANDS:
  "Hey Aria"                    Wake word
  "Find [companies/people]..."  Start research
  "What's your status?"         Progress update
  "Pause/Resume"               Control research
  "Be quiet/Speak up"          Toggle voice

TIPS:
  • Aria saves checkpoints - research can be resumed if interrupted
  • Use Tab completion for commands (if available)
  • Logs are saved to logs/ directory
  • Reports are saved to output/ directory
"""
        
        if console:
            console.print(Panel(help_text, title="Aria Help", border_style="blue"))
        else:
            print(help_text)
    
    async def conversation_mode(self):
        """Interactive conversation mode."""
        greeting = self.personality.greet()
        self.output(greeting, style="aria")
        
        while True:
            try:
                # Get input (voice or text)
                if self.voice_enabled and self.voice:
                    user_input = await self.voice.listen()
                    if not user_input:
                        continue
                else:
                    user_input = input("\nYou: ").strip()
                
                # Check for commands
                if user_input.startswith('/'):
                    await self.handle_command(user_input)
                    continue
                
                # Check for exit
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    self.output("Goodbye! Your research reports are in the output/ directory.", 
                              style="aria")
                    break
                
                # Process research request
                if any(word in user_input.lower() for word in ['find', 'research', 'look for', 'search']):
                    await self.start_research(user_input)
                else:
                    # General conversation
                    response = self.personality.respond(user_input)
                    self.output(response, style="aria")
                    
            except KeyboardInterrupt:
                self.output("\nUse /exit to quit properly.", style="info")
            except Exception as e:
                self.output(f"Error: {e}", style="error")
    
    async def start_research(self, request: str):
        """Start a research task from natural language."""
        # Build assignment through conversation
        assignment = await self.build_assignment(request)
        
        if not assignment:
            return
        
        # Confirm with user
        self.output(f"I'll research: {assignment['title']}", style="aria")
        confirm = input("Should I start? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            self.output("Okay, let me know what else you'd like to research.", style="aria")
            return
        
        # Start research with live updates
        self.is_researching = True
        self.output("Starting research...", style="aria")
        
        # Save assignment for the research engine
        assignment_path = Path('temp_assignment.yaml')
        import yaml
        with open(assignment_path, 'w') as f:
            yaml.dump(assignment, f)
        
        try:
            # Run research with progress updates
            await self.run_research_with_updates(assignment_path)
        finally:
            self.is_researching = False
            # Clean up temp file
            if assignment_path.exists():
                assignment_path.unlink()
    
    async def build_assignment(self, initial_request: str) -> Optional[dict]:
        """Build research assignment through conversation."""
        assignment = {
            'title': '',
            'objectives': [],
            'depth': 'comprehensive',
            'priority': 'normal'
        }
        
        # Determine research type
        if 'compan' in initial_request.lower():
            return await self.templates.company_research_interview(initial_request, self)
        elif 'grant' in initial_request.lower():
            return await self.templates.grant_research_interview(initial_request, self)
        elif 'people' in initial_request.lower() or 'person' in initial_request.lower():
            return await self.templates.people_research_interview(initial_request, self)
        else:
            # General research
            assignment['title'] = initial_request
            
            # Ask for more details
            self.output("What specific information do you need?", style="aria")
            details = input("You: ").strip()
            
            assignment['objectives'] = [
                initial_request,
                details
            ]
            
            return assignment
    
    async def run_research_with_updates(self, assignment_path: Path):
        """Run research with live progress updates and observations."""
        
        # Progress tracking
        start_time = datetime.now()
        
        # Callbacks for real-time updates
        async def progress_callback(stats: dict):
            """Update progress display."""
            elapsed = (datetime.now() - start_time).seconds
            minutes = elapsed // 60
            
            if console and RICH_AVAILABLE:
                progress_text = (
                    f"[bold]Research Progress[/bold]\n"
                    f"Time: {minutes}m {elapsed % 60}s | "
                    f"Companies: {stats.get('companies_found', 0)} | "
                    f"People: {stats.get('people_found', 0)} | "
                    f"Patterns: {stats.get('patterns_detected', 0)}"
                )
                console.print(progress_text)
            else:
                print(f"\rProgress: {minutes}m - {stats.get('companies_found', 0)} companies found", end='')
        
        async def observation_callback(observation: str):
            """Handle Aria's observations."""
            self.output(observation, style="observation")
        
        # Run research with integration
        reports = await self.research_integration.process_with_observations(
            assignment_path,
            progress_callback=progress_callback,
            observation_callback=observation_callback
        )
        
        # Final statistics
        duration = (datetime.now() - start_time).seconds // 60
        stats = self.research_integration.get_progress_stats()
        stats['duration_minutes'] = duration
        
        # Generate completion message
        completion_msg = self.personality.research_complete_message(stats)
        self.output(completion_msg, style="success")
        
        for report in reports:
            self.output(f"📄 Report saved to: {report}", style="info")
        
        # Add to history
        self._add_to_history(assignment_path.stem, reports)
        
        # Show preview
        if reports and console:
            with open(reports[0], 'r') as f:
                preview = f.read()[:500] + "..."
                console.print(Panel(preview, title="Report Preview", border_style="green"))
    
    async def handle_command(self, command: str):
        """Handle slash commands."""
        cmd = command.lower().strip()
        
        if cmd == '/help':
            self.show_help()
        elif cmd == '/history':
            self.show_history()
        elif cmd == '/mute':
            self.muted = not self.muted
            self.output(f"Voice output {'muted' if self.muted else 'enabled'}.", style="info")
        elif cmd == '/clear':
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
        elif cmd in ['/exit', '/quit']:
            sys.exit(0)
        elif cmd == '/status':
            if self.is_researching:
                stats = self.research_integration.get_progress_stats()
                status_msg = (
                    f"Research in progress... "
                    f"Found {stats['companies_found']} companies, "
                    f"{stats['people_found']} people"
                )
                self.output(status_msg, style="info")
            else:
                self.output("Ready for new research.", style="info")
        else:
            self.output(f"Unknown command: {command}", style="error")
    
    def show_history(self):
        """Show research history."""
        if not self.research_history:
            self.output("No research history yet.", style="info")
            return
        
        if console:
            table = Table(title="Research History")
            table.add_column("Date", style="cyan")
            table.add_column("Research", style="white")
            table.add_column("Reports", style="green")
            
            for entry in self.research_history[-10:]:
                table.add_row(
                    entry['date'],
                    entry['title'][:50] + '...' if len(entry['title']) > 50 else entry['title'],
                    str(len(entry['reports']))
                )
            
            console.print(table)
        else:
            print("\nRecent Research:")
            for entry in self.research_history[-10:]:
                print(f"  {entry['date']}: {entry['title'][:50]}...")
    
    def _load_history(self) -> list:
        """Load research history."""
        history_file = Path('aria_history.json')
        if history_file.exists():
            with open(history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _add_to_history(self, title: str, reports: list):
        """Add entry to research history."""
        entry = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'title': title,
            'reports': [str(r) for r in reports]
        }
        self.research_history.append(entry)
        
        # Save history
        with open('aria_history.json', 'w') as f:
            json.dump(self.research_history, f, indent=2)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Aria - AI Research Assistant",
        add_help=False  # We'll handle help ourselves
    )
    
    parser.add_argument('--voice', action='store_true', help='Enable voice mode')
    parser.add_argument('--accent', default='default', 
                       choices=['irish', 'british', 'default'],
                       help='Voice accent')
    parser.add_argument('--hybrid', action='store_true', 
                       help='Voice input with text + voice output')
    parser.add_argument('--quick', help='Quick research task')
    parser.add_argument('--resume', action='store_true', help='Resume last research')
    parser.add_argument('--daemon', action='store_true', help='Run in background')
    parser.add_argument('--mute', action='store_true', help='Start with voice muted')
    parser.add_argument('--help', '-h', action='store_true', help='Show help')
    
    args = parser.parse_args()
    
    # Handle help
    if args.help:
        aria = Aria()
        aria.show_help()
        return
    
    # Create Aria instance
    aria = Aria(
        voice_enabled=args.voice or args.hybrid,
        voice_accent=args.accent,
        hybrid_mode=args.hybrid
    )
    
    if args.mute:
        aria.muted = True
    
    # Handle different modes
    if args.quick:
        # Quick research mode
        await aria.templates.quick_research(args.quick, aria)
    elif args.resume:
        # Resume from checkpoint
        aria.output("Resuming last research...", style="info")
        # TODO: Implement checkpoint resume
    elif args.daemon:
        # Background mode
        aria.output("Running in background mode...", style="info")
        # TODO: Implement daemon mode
    else:
        # Interactive conversation mode
        await aria.conversation_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
