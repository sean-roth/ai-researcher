"""
Quick research templates for common tasks.
"""

from typing import Dict, Optional
import re


class QuickTemplates:
    """Pre-built templates for common research tasks."""
    
    def __init__(self):
        self.templates = {
            'competitors': {
                'title': 'Competitor Analysis',
                'questions': [
                    "What industry are you in?",
                    "What's your company size?",
                    "Which geographic markets?",
                    "Any specific competitors to focus on?"
                ]
            },
            'leads': {
                'title': 'Lead Generation',
                'questions': [
                    "Describe your ideal customer (industry, size, etc.)",
                    "What geographic regions?",
                    "What specific pain points do they have?",
                    "How many leads do you need?"
                ]
            },
            'grants': {
                'title': 'Grant Research',
                'questions': [
                    "What's your business focus?",
                    "What's your location?",
                    "What stage is your company (startup, growth, etc.)?",
                    "Any specific grant programs in mind?"
                ]
            },
            'ideas': {
                'title': 'Business Idea Validation',
                'questions': [
                    "What's the business idea?",
                    "What industry/market?",
                    "B2B or B2C?",
                    "What's your budget range?"
                ]
            },
            'people': {
                'title': 'People/Decision Maker Research',
                'questions': [
                    "What types of people (titles/roles)?",
                    "Which companies or industries?",
                    "What geographic regions?",
                    "Any specific criteria?"
                ]
            },
            'market': {
                'title': 'Market Analysis',
                'questions': [
                    "What market/industry?",
                    "Geographic scope?",
                    "Specific aspects to analyze (size, growth, trends)?",
                    "Time frame for data?"
                ]
            }
        }
    
    def parse_number_from_text(self, text: str) -> int:
        """Parse numbers from natural language."""
        text = text.lower().strip()
        
        # Direct number words
        word_to_num = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'fifteen': 15, 'twenty': 20,
            'thirty': 30, 'forty': 40, 'fifty': 50,
            'hundred': 100, 'thousand': 1000
        }
        
        # Check for word numbers
        for word, num in word_to_num.items():
            if word in text:
                # Handle "a hundred", "a thousand"
                if 'a ' + word in text:
                    return num
                return num
        
        # Try to extract numeric digits
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        # Default based on context
        if 'all' in text or 'many' in text:
            return 20
        elif 'few' in text:
            return 5
        else:
            return 10  # default
    
    async def quick_research(self, template_name: str, aria_instance):
        """Execute a quick research template."""
        if template_name not in self.templates:
            aria_instance.output(f"Unknown template: {template_name}", style="error")
            aria_instance.output("Available templates: " + ", ".join(self.templates.keys()), style="info")
            return None
        
        template = self.templates[template_name]
        aria_instance.output(f"Starting {template['title']}...", style="aria")
        
        # Build assignment through Q&A
        assignment = {
            'title': template['title'],
            'objectives': [],
            'depth': 'comprehensive',
            'priority': 'normal'
        }
        
        # Ask template questions
        answers = []
        for question in template['questions']:
            aria_instance.output(question, style="aria")
            
            # Get answer - use voice if enabled
            if aria_instance.voice_enabled and aria_instance.voice:
                answer = await aria_instance.voice.listen(timeout=7.0)  # Longer timeout
                if not answer:
                    aria_instance.output("I didn't catch that. Let me ask again.", style="aria")
                    answer = await aria_instance.voice.listen(timeout=7.0)
            else:
                answer = input("You: ").strip()
            
            if answer:
                answers.append(answer)
        
        # Build objectives from answers
        if template_name == 'competitors':
            assignment['objectives'] = [
                f"Find competitors in {answers[0]} industry",
                f"Focus on {answers[1]} sized companies",
                f"In {answers[2]} markets"
            ]
            if len(answers) > 3:
                assignment['objectives'].append(f"Especially analyze {answers[3]}")
                
        elif template_name == 'leads':
            assignment['objectives'] = [
                f"Find {answers[3] if len(answers) > 3 else '20'} potential leads",
                f"Target: {answers[0]}",
                f"In {answers[1]}",
                f"With pain points: {answers[2]}"
            ]
            
        elif template_name == 'grants':
            assignment['objectives'] = [
                f"Find grants for {answers[0]} businesses",
                f"Located in {answers[1]}",
                f"At {answers[2]} stage"
            ]
            
        elif template_name == 'people':
            assignment['objectives'] = [
                f"Find {answers[0]}",
                f"At {answers[1]}",
                f"In {answers[2]}"
            ]
            if len(answers) > 3:
                assignment['objectives'].append(f"Criteria: {answers[3]}")
        
        return assignment
    
    async def company_research_interview(self, initial_request: str, aria_instance) -> Dict:
        """Specialized interview for company research."""
        aria_instance.output("Company research - let me understand what you need.", style="aria")
        
        # Key questions - now with voice support
        questions = [
            ("What type of companies? (e.g., Japanese tech, US startups)", "company_type"),
            ("Company size? (e.g., 50-500, enterprise, any)", "company_size"),
            ("What specific information do you need? (pricing/contacts/challenges/all)", "specifics"),
            ("How many companies should I find?", "count")
        ]
        
        answers = {}
        
        for question, key in questions:
            aria_instance.output(question, style="aria")
            
            # Get answer with voice support
            if aria_instance.voice_enabled and aria_instance.voice:
                answer = await aria_instance.voice.listen(timeout=7.0)
                if not answer:
                    aria_instance.output("I didn't catch that. Let me ask again.", style="aria")
                    answer = await aria_instance.voice.listen(timeout=7.0)
            else:
                answer = input("You: ").strip()
            
            answers[key] = answer
        
        # Parse count with natural language support
        try:
            count = self.parse_number_from_text(answers.get('count', '10'))
        except:
            count = 10
            aria_instance.output(f"I'll find {count} companies.", style="aria")
        
        # Build assignment
        assignment = {
            'title': f"Company Research: {answers.get('company_type', 'companies')}",
            'objectives': [
                f"Find {count} {answers.get('company_type', '')} companies",
                f"Company size: {answers.get('company_size', 'any')}",
                f"Focus on: {answers.get('specifics', 'all information')}"
            ],
            'depth': 'comprehensive' if count < 50 else 'balanced',
            'priority': 'normal'
        }
        
        # Add any special criteria from initial request
        if 'english' in initial_request.lower():
            assignment['objectives'].append("Identify English training needs")
        if 'competitor' in initial_request.lower():
            assignment['objectives'].append("Analyze as potential competitors")
        if 'client' in initial_request.lower():
            assignment['objectives'].append("Evaluate as potential clients")
            
        return assignment
    
    async def grant_research_interview(self, initial_request: str, aria_instance) -> Dict:
        """Specialized interview for grant research."""
        aria_instance.output("Grant research - I'll help you find funding opportunities.", style="aria")
        
        questions = [
            ("What's your business focus?", "focus"),
            ("Your location? (city, state/country)", "location"),
            ("Company stage? (pre-revenue, seed, growth, etc.)", "stage"),
            ("Any specific focus areas? (R&D, hiring, equipment, etc.)", "areas")
        ]
        
        answers = {}
        
        for question, key in questions:
            aria_instance.output(question, style="aria")
            
            if aria_instance.voice_enabled and aria_instance.voice:
                answer = await aria_instance.voice.listen(timeout=7.0)
                if not answer:
                    aria_instance.output("I didn't catch that. Let me ask again.", style="aria")
                    answer = await aria_instance.voice.listen(timeout=7.0)
            else:
                answer = input("You: ").strip()
                
            answers[key] = answer
        
        assignment = {
            'title': f"Grant Research: {answers.get('focus', 'business')}",
            'objectives': [
                f"Find grants for {answers.get('focus', 'business')} businesses",
                f"Available in {answers.get('location', 'any location')}",
                f"For {answers.get('stage', 'any')} stage companies",
                f"Focus on {answers.get('areas', 'all types')} grants" if answers.get('areas') else "All types of grants"
            ],
            'depth': 'comprehensive',
            'priority': 'high'
        }
        
        return assignment
    
    async def people_research_interview(self, initial_request: str, aria_instance) -> Dict:
        """Specialized interview for people/decision maker research."""
        aria_instance.output("Looking for specific people - let me get the details.", style="aria")
        
        questions = [
            ("What roles/titles? (e.g., HR Director, CTO, etc.)", "roles"),
            ("At what types of companies?", "companies"),
            ("Geographic focus? (any, specific city/country)", "geography"),
            ("Any other criteria? (company size, industry, etc.)", "criteria")
        ]
        
        answers = {}
        
        for question, key in questions:
            aria_instance.output(question, style="aria")
            
            if aria_instance.voice_enabled and aria_instance.voice:
                answer = await aria_instance.voice.listen(timeout=7.0)
                if not answer:
                    aria_instance.output("I didn't catch that. Let me ask again.", style="aria")
                    answer = await aria_instance.voice.listen(timeout=7.0)
            else:
                answer = input("You: ").strip()
                
            answers[key] = answer
        
        assignment = {
            'title': f"Decision Maker Research: {answers.get('roles', 'people')}",
            'objectives': [
                f"Find {answers.get('roles', 'decision makers')}",
                f"At {answers.get('companies', 'companies')}",
                f"Located in {answers.get('geography', 'any location')}"
            ],
            'depth': 'comprehensive',
            'priority': 'normal'
        }
        
        if answers.get('criteria'):
            assignment['objectives'].append(f"Additional criteria: {answers['criteria']}")
            
        return assignment
