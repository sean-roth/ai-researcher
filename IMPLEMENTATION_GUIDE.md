# Implementation Guide for Claude Code

## Quick Start Implementation Steps

### Step 1: Gmail API Setup (Priority 1)
```bash
# First, create a new file for Gmail setup
touch src/setup_gmail.py
```

1. Go to https://console.cloud.google.com
2. Create new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials.json to `credentials/` folder
6. Run setup script to authenticate

### Step 2: Create Email Agent (Priority 1)
Start with `src/email_agent.py`:
- Basic send functionality
- Rate limiting (20/day)
- Response checking
- Simple logging

### Step 3: Extend Research Engine (Priority 2)
Modify `src/research_engine.py`:
- Add company scoring
- Filter by size (50-500 employees)
- Focus on English training signals

### Step 4: Create Campaign Assignment (Priority 2)
Create `examples/assignments/compel_english_campaign.yaml`:
```yaml
title: "Compel English - Japanese Tech Companies Outreach"
campaign_type: "b2b_sales"
product: "Compel English - AI Pronunciation Coach"

targeting:
  industries: ["Technology", "Finance"]
  company_size: [50, 500]
  geography: "Japan"
  
objectives:
  - "Find companies with English requirements in job posts"
  - "Identify L&D/HR decision makers"
  - "Score English training need (1-10)"
  
email_settings:
  daily_limit: 20
  follow_up_days: [3, 7, 14]
  from_name: "Sean Roth"
  from_email: "sean@altdomain.com"
```

### Step 5: Safety & Blacklist (Priority 3)
Create `src/blacklist_manager.py`:
- Simple domain blacklist
- Competitor filter
- Recent contact check

## Testing Sequence

1. **Test Gmail Connection**
   ```python
   python -m src.email_agent test_connection
   ```

2. **Test Single Email Send**
   ```python
   python -m src.email_agent test_send --to=your-test@email.com
   ```

3. **Test Research + Scoring**
   ```python
   python test_research.py --company "Rakuten" --score-for-english
   ```

4. **Test Full Pipeline (Dry Run)**
   ```python
   python run_campaign.py --dry-run --limit=1
   ```

## Key Files to Create/Modify

### New Files Needed:
1. `src/email_agent.py` - Gmail integration
2. `src/lead_enricher.py` - Company scoring  
3. `src/blacklist_manager.py` - Do not contact list
4. `src/setup_gmail.py` - OAuth setup helper
5. `credentials/.gitkeep` - For credentials folder

### Files to Modify:
1. `src/research_engine.py` - Add sales focus
2. `config.yaml` - Add email settings
3. `requirements.txt` - Add new dependencies

## Dependencies to Add:
```txt
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
aiogmail  # for async operations
```

## Important Notes for Claude Code:

1. **Start Small**: Get basic email sending working first
2. **Use Test Data**: Use your own test email addresses initially  
3. **Dry Run Mode**: Always include --dry-run option for testing
4. **Logging**: Add extensive logging for debugging
5. **Error Handling**: Gmail API can be flaky, add retries

## Questions to Resolve:

1. Do we want async email operations (aiogmail) or sync?
2. Should templates be in Python or YAML files?
3. How should we handle email threading/conversations?
4. Do we need a separate service for monitoring responses?

## Example Code Structure for Email Agent:

```python
# src/email_agent.py
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class EmailAgent:
    def __init__(self, credentials_path):
        self.service = self._authenticate(credentials_path)
        self.daily_sends = {}
        
    def send_email(self, to, subject, body, from_alias=None):
        # Check daily limits
        # Construct message
        # Send via API
        # Log to database
        pass
        
    def check_responses(self):
        # Get messages since last check
        # Classify responses
        # Update company status
        pass
```

Start with Step 1 and work through sequentially. The design document has all the details you need for each component.