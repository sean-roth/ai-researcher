"""
Prompt management system for Aria.
Loads and manages structured prompts to keep the 8B model focused.
"""

from pathlib import Path
from typing import Dict, Optional
import yaml


class PromptLibrary:
    """Manages structured prompts for different research tasks."""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.loaded_prompts = {}
        self._load_all_prompts()
    
    def _load_all_prompts(self):
        """Load all prompts from the prompts directory."""
        if not self.prompts_dir.exists():
            print(f"Prompts directory not found: {self.prompts_dir}")
            return
        
        # Load research prompts
        research_dir = self.prompts_dir / "research"
        if research_dir.exists():
            for prompt_file in research_dir.glob("*.md"):
                prompt_name = f"research/{prompt_file.stem}"
                self.loaded_prompts[prompt_name] = prompt_file.read_text()
        
        # Load extraction prompts
        extraction_dir = self.prompts_dir / "extraction"
        if extraction_dir.exists():
            for prompt_file in extraction_dir.glob("*.md"):
                prompt_name = f"extraction/{prompt_file.stem}"
                self.loaded_prompts[prompt_name] = prompt_file.read_text()
        
        # Load special prompts
        special_dir = self.prompts_dir / "special"
        if special_dir.exists():
            for prompt_file in special_dir.glob("*.md"):
                prompt_name = f"special/{prompt_file.stem}"
                self.loaded_prompts[prompt_name] = prompt_file.read_text()
        
        print(f"Loaded {len(self.loaded_prompts)} prompts")
    
    def get_prompt(self, prompt_name: str) -> Optional[str]:
        """Get a specific prompt by name."""
        return self.loaded_prompts.get(prompt_name)
    
    def get_research_prompt(self, research_type: str, context: Dict) -> str:
        """Get a research prompt with context filled in."""
        # Map research types to prompt names
        prompt_map = {
            'leads': 'research/lead_generation',
            'lead': 'research/lead_generation',
            'companies': 'research/lead_generation',
            'competitor': 'research/competitor_analysis',
            'competitors': 'research/competitor_analysis',
            'grant': 'research/grant_research',
            'grants': 'research/grant_research',
            'market': 'research/market_analysis',
            'course': 'special/course_creation',
            'training': 'special/course_creation'
        }
        
        # Find the right prompt
        prompt_name = prompt_map.get(research_type.lower(), 'research/lead_generation')
        base_prompt = self.get_prompt(prompt_name)
        
        if not base_prompt:
            # Fallback to a generic prompt
            return self._generic_research_prompt(context)
        
        # Add context to the prompt
        enhanced_prompt = f"{base_prompt}\n\n## Specific Context for This Research\n"
        
        if context.get('company_type'):
            enhanced_prompt += f"- Focus on: {context['company_type']}\n"
        if context.get('location'):
            enhanced_prompt += f"- Geographic focus: {context['location']}\n"
        if context.get('company_size'):
            enhanced_prompt += f"- Company size: {context['company_size']}\n"
        if context.get('objectives'):
            enhanced_prompt += f"- Objectives: {', '.join(context['objectives'])}\n"
        
        return enhanced_prompt
    
    def _generic_research_prompt(self, context: Dict) -> str:
        """Fallback generic research prompt."""
        return f"""
You are conducting research to find specific information.

## Objectives
{chr(10).join('- ' + obj for obj in context.get('objectives', ['Conduct thorough research']))}

## Requirements
- Find specific, actionable information
- Include company names and contact details where applicable
- Verify information is recent and accurate
- Provide sources for all claims

## Output Format
Organize your findings clearly with:
1. Company/Organization name
2. Relevant details
3. Contact information if available
4. Source URLs

Focus on quality over quantity. Be specific and thorough.
"""
    
    def get_extraction_prompt(self, extraction_type: str) -> str:
        """Get an extraction prompt for processing raw content."""
        prompt_name = f"extraction/{extraction_type}"
        return self.get_prompt(prompt_name) or self._generic_extraction_prompt()
    
    def _generic_extraction_prompt(self) -> str:
        """Fallback extraction prompt."""
        return """
Extract relevant information from the provided content.

Focus on:
- Company names and details
- People names and titles
- Specific needs or challenges mentioned
- Contact information
- Relevant quotes or data points

Return extracted information in a structured format.
"""
    
    def list_available_prompts(self) -> Dict[str, list]:
        """List all available prompts by category."""
        categories = {}
        for prompt_name in self.loaded_prompts:
            category, name = prompt_name.split('/', 1)
            if category not in categories:
                categories[category] = []
            categories[category].append(name)
        return categories
    
    def save_new_prompt(self, category: str, name: str, content: str):
        """Save a new prompt to the library."""
        prompt_dir = self.prompts_dir / category
        prompt_dir.mkdir(exist_ok=True)
        
        prompt_file = prompt_dir / f"{name}.md"
        prompt_file.write_text(content)
        
        # Reload prompts
        self._load_all_prompts()
        print(f"Saved new prompt: {category}/{name}")
