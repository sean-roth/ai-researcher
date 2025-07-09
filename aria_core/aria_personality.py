"""
Aria's personality module - handles observations, responses, and character.
"""

import random
from typing import Dict, List, Optional
from datetime import datetime


class AriaPersonality:
    """Aria's personality - competent, observant, subtly warm."""
    
    def __init__(self):
        self.observations_made = []
        self.last_observation_time = None
        self.observation_cooldown = 120  # seconds between observations
        
        # Personality traits
        self.traits = {
            'core': 'thorough researcher who notices patterns',
            'communication': 'clear, warm but professional',
            'curiosity': 'genuine interest in data patterns',
            'humor': 'dry observations when natural'
        }
        
        # Different types of observations Aria might make
        self.observation_types = {
            'pattern': [
                "Noticing a pattern - {detail}",
                "Interesting cluster here - {detail}",
                "{count} companies in a row with {pattern}",
                "This keeps coming up - {detail}"
            ],
            'timing': [
                "Curious timing - {detail}",
                "All posted within {timeframe}",
                "Surge of activity in {period}",
                "{event} seems to have triggered this"
            ],
            'outlier': [
                "{company} is an outlier - {reason}",
                "This one's different - {detail}",
                "Unexpected find - {detail}",
                "{company} doesn't fit the pattern"
            ],
            'connection': [
                "Wait, {person} used to work at {previous_company}",
                "These companies share {connection}",
                "Found a link - {detail}",
                "Same {attribute} across multiple results"
            ],
            'insight': [
                "Might be {hypothesis}",
                "This suggests {conclusion}",
                "Could indicate {trend}",
                "Possibly related to {event}"
            ]
        }
        
        # Greetings
        self.greetings = [
            "Morning. What are we investigating today?",
            "Ready when you are.",
            "What's the research focus today?",
            "Let's find what you need.",
            "What should I look into?"
        ]
        
        # Status updates
        self.status_updates = [
            "About {percent}% through. Finding good leads in {area}.",
            "Still searching. Best find so far: {detail}",
            "{time} minutes in - {number} solid matches.",
            "Making progress. {observation}",
            "{number} companies found. Looking for more."
        ]
    
    def greet(self) -> str:
        """Return a greeting."""
        greeting = random.choice(self.greetings)
        hour = datetime.now().hour
        
        # Adjust greeting based on time
        if hour < 12:
            return greeting
        elif hour < 17:
            return greeting.replace("Morning", "Afternoon")
        else:
            return greeting.replace("Morning", "Evening")
    
    def make_observation(self, context: Dict) -> Optional[str]:
        """Make an observation based on research findings."""
        # Check cooldown
        if self.last_observation_time:
            elapsed = (datetime.now() - self.last_observation_time).seconds
            if elapsed < self.observation_cooldown:
                return None
        
        # Determine observation type based on context
        obs_type = self._determine_observation_type(context)
        if not obs_type:
            return None
        
        # Select appropriate template
        templates = self.observation_types[obs_type]
        template = random.choice(templates)
        
        # Fill in the template
        observation = template.format(**context)
        
        # Record observation
        self.observations_made.append({
            'time': datetime.now(),
            'type': obs_type,
            'observation': observation
        })
        self.last_observation_time = datetime.now()
        
        return observation
    
    def _determine_observation_type(self, context: Dict) -> Optional[str]:
        """Determine what type of observation to make."""
        # Pattern detection
        if context.get('pattern_count', 0) >= 3:
            return 'pattern'
        
        # Timing observations
        if context.get('time_correlation'):
            return 'timing'
        
        # Outlier detection
        if context.get('is_outlier'):
            return 'outlier'
        
        # Connection finding
        if context.get('connection_found'):
            return 'connection'
        
        # General insights
        if context.get('significance', 0) > 0.7:
            return 'insight'
        
        return None
    
    def respond(self, user_input: str) -> str:
        """Generate a response to user input."""
        input_lower = user_input.lower()
        
        # Status queries
        if any(word in input_lower for word in ['status', 'progress', 'how are you doing']):
            return self._status_response()
        
        # Affirmations
        if any(word in input_lower for word in ['good', 'great', 'nice', 'excellent']):
            return random.choice([
                "Let me know what else you need.",
                "What's next?",
                "Ready for another search.",
                "Anything else to research?"
            ])
        
        # Questions about findings
        if any(word in input_lower for word in ['tell me more', 'what else', 'details']):
            return "I'll dig deeper into that."
        
        # Default
        return "What would you like me to research?"
    
    def _status_response(self) -> str:
        """Generate a status response."""
        if self.observations_made:
            last_obs = self.observations_made[-1]['observation']
            return f"Still researching. Recent observation: {last_obs}"
        else:
            return "Ready to start researching."
    
    def format_finding(self, company: str, detail: str, significance: float) -> str:
        """Format a finding announcement."""
        if significance > 0.8:
            templates = [
                f"Good find - {company}: {detail}",
                f"This is relevant - {company}: {detail}",
                f"{company} stands out: {detail}"
            ]
        elif significance > 0.5:
            templates = [
                f"Found {company} - {detail}",
                f"Adding {company}: {detail}",
                f"{company} matches: {detail}"
            ]
        else:
            templates = [
                f"{company} - {detail}",
                f"Noted {company}",
                f"Added {company} to the list"
            ]
        
        return random.choice(templates)
    
    def research_complete_message(self, stats: Dict) -> str:
        """Generate research completion message."""
        companies = stats.get('companies_found', 0)
        people = stats.get('people_found', 0)
        duration = stats.get('duration_minutes', 0)
        
        base_message = f"Research complete. Found {companies} companies"
        
        if people > 0:
            base_message += f" and {people} decision makers"
        
        base_message += f" in {duration} minutes."
        
        # Add an observation if we found something interesting
        if companies > 20:
            base_message += " Quite a productive search."
        elif companies < 5:
            base_message += " Narrow criteria, but quality matches."
        
        return base_message
    
    def get_thinking_aloud_prompt(self) -> str:
        """Return instructions for thinking aloud during research."""
        return """
As you research, think aloud about:
- Patterns you notice across results
- Timing coincidences or clusters  
- Companies or people that stand out as unusual
- Potential connections between findings
- Hypotheses about why certain patterns exist

Don't force observations - only mention what genuinely stands out in the data.
Think like a detective noticing clues, not a tour guide describing everything.
"""
