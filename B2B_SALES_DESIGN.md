# B2B Sales Outreach Extension - Design Document

## Overview
Transform the AI Researcher into "Aria" - an autonomous B2B sales outreach agent for Compel English, targeting Japanese tech companies (50-500 employees) that need English training solutions.

## Core Architecture Extensions

### 1. Email Integration Module (`src/email_agent.py`)
```python
class EmailAgent:
    """
    Manages all email operations with Gmail API
    - Sends personalized outreach emails
    - Monitors responses and classifies them
    - Manages follow-up sequences
    - Respects rate limits (20/day/inbox)
    """
    
    def __init__(self, credentials_path):
        self.gmail_service = self._build_gmail_service(credentials_path)
        self.daily_sends = {}  # Track sends per inbox
        
    async def send_email(self, to, subject, body, from_inbox):
        # Check daily limits
        # Send via Gmail API
        # Log to database
        pass
        
    async def check_responses(self):
        # Poll for new emails
        # Classify: interested/questions/not_interested/out_of_office
        # Update CRM
        pass
```

### 2. Lead Enrichment & Scoring (`src/lead_enricher.py`)
```python
class LeadEnricher:
    """
    Converts raw research into actionable sales intelligence
    """
    
    def score_company(self, research_data):
        # Score 1-10 based on:
        # - English requirements in job posts
        # - International expansion signals
        # - Team size and growth
        # - Current solutions (if any)
        # - Budget indicators
        return pain_score, confidence_level
        
    def identify_decision_makers(self, company_data):
        # Find: HR Directors, L&D Managers, CTOs
        # Extract: Name, Title, LinkedIn, Email patterns
        return contacts
```

### 3. RAG Builder (`src/rag_builder.py`)
```python
class CompanyRAG:
    """
    Creates and maintains a knowledge base for each prospect
    """
    
    def __init__(self, company_name, obsidian_vault_path):
        self.company = company_name
        self.vault_path = obsidian_vault_path
        self.vector_store = self._init_vectors()
        
    def add_research(self, findings):
        # Convert to embeddings
        # Store in vector database
        # Update Obsidian markdown
        pass
        
    def query(self, question):
        # Semantic search over company knowledge
        # Return relevant context for email generation
        pass
```

### 4. Campaign Manager (`src/campaign_manager.py`)
```python
class CampaignManager:
    """
    Orchestrates the entire sales process
    """
    
    def __init__(self, config):
        self.research_engine = ResearchEngine(config)
        self.email_agent = EmailAgent(config['gmail_creds'])
        self.lead_enricher = LeadEnricher()
        self.blacklist = BlacklistManager()
        
    async def run_campaign(self, assignment):
        # 1. Research companies
        # 2. Score and filter
        # 3. Build RAGs
        # 4. Generate email sequences
        # 5. Send emails (respecting limits)
        # 6. Monitor responses
        # 7. Trigger follow-ups or escalations
        pass
```

### 5. Obsidian Integration (`src/obsidian_sync.py`)
```python
class ObsidianVault:
    """
    Manages the sales intelligence vault
    """
    
    def __init__(self, vault_path, sync_to_gdrive=True):
        self.vault_path = Path(vault_path)
        self.gdrive_sync = sync_to_gdrive
        
    def create_company_note(self, company_data):
        # Create structured markdown
        # Include research audit trail
        # Link to contacts
        # Track email history
        pass
        
    def update_dashboard(self, daily_stats):
        # Update main dashboard with metrics
        # List action items
        # Show top prospects
        pass
```

### 6. Safety & Compliance (`src/safety_manager.py`)
```python
class SafetyManager:
    """
    Ensures ethical and safe email generation
    """
    
    def __init__(self):
        self.blacklist = self._load_blacklist()
        self.suppression_list = self._load_suppressions()
        self.email_templates = self._load_approved_templates()
        
    def check_email_safety(self, email_content):
        # No medical/legal/financial advice
        # No promises beyond actual offering
        # No prompt injections in output
        # Verify claims match Compel English features
        return is_safe, issues
        
    def is_blacklisted(self, company_domain):
        # Check against do-not-contact list
        # Check suppression reasons
        # Check competitor list
        return is_blacklisted, reason
```

### 7. Voice Interface (`src/voice_interface.py`)
```python
class AriaVoiceInterface:
    """
    Natural language interface to Aria while she works
    """
    
    def __init__(self):
        self.commands = VoiceCommandParser()
        self.status_monitor = StatusMonitor()
        
    async def process_voice_command(self, audio_buffer):
        # Transcribe with Whisper
        # Parse intent
        # Execute command
        # Respond with status
        pass
```

## Data Storage Architecture

### SQLite Database Schema
```sql
-- companies.db
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT UNIQUE NOT NULL,
    industry TEXT,
    size_estimate INTEGER,
    location TEXT,
    pain_score INTEGER,
    research_date DATE,
    last_contact_date DATE,
    status TEXT CHECK(status IN ('researching', 'qualified', 'contacted', 'responded', 'customer', 'lost', 'blacklisted')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    name TEXT NOT NULL,
    title TEXT,
    email TEXT,
    linkedin_url TEXT,
    decision_maker_type TEXT,
    last_contacted DATE
);

CREATE TABLE email_interactions (
    id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    contact_id INTEGER REFERENCES contacts(id),
    direction TEXT CHECK(direction IN ('sent', 'received')),
    subject TEXT,
    body TEXT,
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    response_classification TEXT
);

CREATE TABLE blacklist (
    id INTEGER PRIMARY KEY,
    domain TEXT UNIQUE NOT NULL,
    reason TEXT,
    added_date DATE,
    added_by TEXT
);
```

### Obsidian Vault Structure
```
Sales Intelligence Vault/
├── 📊 Dashboard.md
├── 🏢 Companies/
│   ├── Active/
│   │   ├── [[Rakuten]].md
│   │   └── [[Mercari]].md
│   ├── Customers/
│   └── Blacklisted/
├── 👥 Contacts/
│   └── [[Taro Yamada - Rakuten CTO]].md
├── 📧 Campaigns/
│   └── 2025-01-Japanese-Tech/
│       ├── Campaign Overview.md
│       ├── Email Templates.md
│       └── Results.md
├── 🚫 Blacklist/
│   └── Do Not Contact.md
└── 📝 Research Logs/
    └── 2025-01-28-Overnight-Run.md
```

## Email Templates for Compel English

### Template 1: Pain Point Approach
```
Subject: Noticed {company}'s English requirements in engineering roles

Hi {name},

I saw {company} posted {number} positions requiring "excellent verbal English" last month. 

Most Japanese professionals have strong grammar but pronunciation undermines their credibility in meetings. We're solving this differently.

Compel English uses thriller narratives (think "The Midnight Margin Call") with AI pronunciation coaching specifically for Japanese speakers. Your team practices through stories, not textbooks.

Worth exploring? Demo launches next month - want early access?

Best,
Sean
```

### Template 2: Expansion Angle
```
Subject: How {company} can support your {market} expansion

Hi {name},

Congratulations on {company}'s expansion into {market}. 

I imagine your team is navigating more English conversations now. We've built something unique for Japanese professionals - thriller stories that teach pronunciation while keeping your team engaged.

No boring corporate training. Just compelling narratives with real-time AI feedback on pronunciation challenges like regulatory terms and client presentations.

Interested in seeing how it works? Free demo available.

Best,
Sean
```

## Implementation Phases

### Phase 1: Core Email Infrastructure (Week 1)
1. Set up Gmail API authentication
2. Build EmailAgent class with send/receive
3. Create basic email templates
4. Test with single inbox
5. Add rate limiting and logging

### Phase 2: Company Intelligence (Week 2)
1. Extend research_engine.py for sales focus
2. Build lead scoring algorithm
3. Create RAG storage system
4. Integrate with Obsidian vault
5. Add deduplication logic

### Phase 3: Campaign Automation (Week 3)
1. Build CampaignManager orchestration
2. Add follow-up sequence logic
3. Implement response classification
4. Create safety checks
5. Add blacklist management

### Phase 4: Voice & Monitoring (Week 4)
1. Add voice command interface
2. Create real-time status dashboard
3. Build audit trail system
4. Add analytics and reporting
5. Polish and optimize

## Configuration Updates

### config.yaml additions:
```yaml
# Email Configuration
gmail:
  credentials_path: "credentials/gmail_creds.json"
  daily_send_limit: 20
  inboxes:
    - email: "sean@altdomain.com"
      name: "Sean Roth"
      signature: "path/to/signature.html"

# Obsidian Configuration  
obsidian:
  vault_path: "G:/My Drive/Sales Intelligence Vault"
  sync_enabled: true
  
# Sales Configuration
sales:
  product_name: "Compel English"
  target_company_size_min: 50
  target_company_size_max: 500
  target_industries:
    - "Technology"
    - "Finance"
    - "Manufacturing"
  pricing:
    demo: 0
    launch_discount: 37.50
    regular: 75.00

# Safety Configuration
safety:
  require_human_review_after: 100
  banned_industries:
    - "Adult Entertainment"
    - "Gambling"
  competitor_domains:
    - "berlitz.com"
    - "ef.com"
```

## Key Success Metrics

1. **Research Quality**
   - Companies found per night: 20+
   - Qualified leads (7+ pain score): 60%
   - Decision makers identified: 3+ per company

2. **Email Performance**
   - Open rate: 40%+
   - Response rate: 20%+
   - Positive response rate: 10%+

3. **Conversion Funnel**
   - Email → Demo signup: 5%
   - Demo → Trial: 30%
   - Trial → Paid: 20%

## Security & Compliance

1. **Data Protection**
   - All research data encrypted at rest
   - Gmail OAuth2 tokens rotated regularly
   - No storage of personal data beyond business contacts

2. **Email Compliance**
   - CAN-SPAM compliant headers
   - Easy unsubscribe mechanism
   - Suppression list honored

3. **Ethical Guidelines**
   - Only research public information
   - Respect "do not contact" requests immediately
   - No deceptive practices
   - Transparent about using AI assistance

## Testing Strategy

1. **Unit Tests**
   - Email sending/receiving
   - Lead scoring algorithm
   - RAG queries
   - Safety checks

2. **Integration Tests**
   - Full campaign flow
   - Obsidian sync
   - Gmail API limits
   - Voice commands

3. **Manual Testing**
   - Email template quality
   - Research accuracy
   - Response classification
   - Dashboard updates

## Deployment Considerations

1. **Local Development**
   - Use test Gmail account
   - Separate Obsidian vault
   - Mock Compel English API

2. **Production**
   - Encrypted credential storage
   - Automated backups
   - Error monitoring
   - Performance metrics

## Next Steps for Claude Code

1. Review this design document
2. Start with `src/email_agent.py` implementation
3. Create Gmail API setup script
4. Build basic email sending functionality
5. Test with a single test email
6. Proceed through phases sequentially

## Questions for Implementation

1. Should we use aiogmail for async Gmail operations?
2. Do we want a web UI or stick with CLI + Obsidian?
3. Should email templates be in YAML or Python?
4. How should we handle email threading?
5. Do we need a separate response handler service?

This design provides a complete blueprint for transforming the AI Researcher into a powerful B2B sales outreach system for Compel English. The modular architecture allows for incremental development while maintaining the core research capabilities.