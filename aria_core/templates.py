"""
Quick research templates for common tasks.
"""

from typing import Dict, Optional


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
        
        # Key questions
        aria_instance.output("What type of companies? (e.g., Japanese tech, US startups)", style="aria")
        company_type = input("You: ").strip()
        
        aria_instance.output("Company size? (e.g., 50-500, enterprise, any)", style="aria")
        company_size = input("You: ").strip()
        
        aria_instance.output("What specific information do you need? (pricing/contacts/challenges/all)", style="aria")
        specifics = input("You: ").strip()
        
        aria_instance.output("How many companies should I find?", style="aria") 
        count = input("You: ").strip()
        
        # Build assignment
        assignment = {
            'title': f"Company Research: {company_type}",
            'objectives': [
                f"Find {count} {company_type} companies",
                f"Company size: {company_size}",
                f"Focus on: {specifics}"
            ],
            'depth': 'comprehensive' if int(count) < 50 else 'balanced',
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
        
        aria_instance.output("What's your business focus?", style="aria")
        focus = input("You: ").strip()
        
        aria_instance.output("Your location? (city, state/country)", style="aria")
        location = input("You: ").strip()
        
        aria_instance.output("Company stage? (pre-revenue, seed, growth, etc.)", style="aria")
        stage = input("You: ").strip()
        
        aria_instance.output("Any specific focus areas? (R&D, hiring, equipment, etc.)", style="aria")
        areas = input("You: ").strip()
        
        assignment = {
            'title': f"Grant Research: {focus}",
            'objectives': [
                f"Find grants for {focus} businesses",
                f"Available in {location}",
                f"For {stage} stage companies",
                f"Focus on {areas} grants" if areas else "All types of grants"
            ],
            'depth': 'comprehensive',
            'priority': 'high'
        }
        
        return assignment
    
    async def people_research_interview(self, initial_request: str, aria_instance) -> Dict:
        """Specialized interview for people/decision maker research."""
        aria_instance.output("Looking for specific people - let me get the details.", style="aria")
        
        aria_instance.output("What roles/titles? (e.g., HR Director, CTO, etc.)", style="aria")
        roles = input("You: ").strip()
        
        aria_instance.output("At what types of companies?", style="aria")
        companies = input("You: ").strip()
        
        aria_instance.output("Geographic focus? (any, specific city/country)", style="aria")
        geography = input("You: ").strip()
        
        aria_instance.output("Any other criteria? (company size, industry, etc.)", style="aria")
        criteria = input("You: ").strip()
        
        assignment = {
            'title': f"Decision Maker Research: {roles}",
            'objectives': [
                f"Find {roles}",
                f"At {companies}",
                f"Located in {geography}"
            ],
            'depth': 'comprehensive',
            'priority': 'normal'
        }
        
        if criteria:
            assignment['objectives'].append(f"Additional criteria: {criteria}")
            
        return assignment
