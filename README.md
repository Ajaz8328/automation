# Zammad to Azure DevOps Automation

Automated workflow for processing Zammad tickets and creating Azure DevOps issues.

## 🎯 Purpose

This automation is part of the **Bobathon Challenge**, demonstrating integration between:
- **Grafana** - Monitoring and alerting
- **Zammad** - Ticketing system
- **Loki** - Log aggregation
- **Azure DevOps** - Issue tracking
- **IBM ICA Context Studio** - Knowledge graph and MCP server

## 📁 Files

- **`zammad_ado_automation.py`** - Main automation script that processes a single ticket
- **`monitor_tickets.py`** - Continuous monitoring agent that checks for new tickets every 30 seconds
- **`list_zammad_tickets.py`** - Helper utility to list available Zammad tickets
- **`check_ado_workitems.py`** - Helper utility to check Azure DevOps work item types

## 🚀 How It Works

### Complete Workflow:

```
1. Grafana detects errors in application logs
   ↓
2. Grafana fires alert with severity:critical
   ↓
3. Alert creates ticket in Zammad
   ↓
4. Monitor script detects new ticket (checks every 30s)
   ↓
5. Automation script processes the ticket:
   - Fetches ticket details from Zammad
   - Queries error logs from Loki
   - Creates issue in Azure DevOps
   - Updates Zammad ticket with ADO link
   ↓
6. Complete audit trail maintained in Context Studio
```

## 🏗️ Architecture

```
┌─────────────┐
│   Grafana   │ (Monitoring)
└──────┬──────┘
       │ Alert
       ▼
┌─────────────┐     ┌─────────────┐
│   Zammad    │────▶│    Loki     │
│  (Tickets)  │     │   (Logs)    │
└──────┬──────┘     └─────────────┘
       │
       │ Monitor
       ▼
┌─────────────┐     ┌─────────────┐
│   GitHub    │────▶│   Context   │
│ (This Repo) │     │   Studio    │
└──────┬──────┘     └──────┬──────┘
       │                   │
       │ MCP Protocol      │
       └───────┬───────────┘
               ▼
       ┌─────────────┐
       │     Bob     │ (AI Agent)
       │   (Agent)   │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐
       │Azure DevOps │
       │  (Issues)   │
       └─────────────┘
```

## 🔧 Setup

### Prerequisites

- Python 3.11 or higher
- Access to Zammad instance
- Azure DevOps account with PAT
- Loki instance (optional, for log collection)
- IBM ICA Context Studio account

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Configuration

Update these variables in the scripts with your credentials:

```python
# In zammad_ado_automation.py and monitor_tickets.py
ZAMMAD_URL = "https://your-instance.zammad.com"
ZAMMAD_TOKEN = "your-zammad-api-token"
LOKI_URL = "http://localhost:3100"
ADO_ORG = "your-ado-organization"
ADO_PROJECT = "your-ado-project"
ADO_PAT = "your-azure-devops-pat"
```

## 📊 Usage

### Option 1: Process a Single Ticket

```bash
python zammad_ado_automation.py [TICKET_ID]

# Example:
python zammad_ado_automation.py 10
```

### Option 2: Continuous Monitoring (Recommended)

```bash
python monitor_tickets.py
```

This will:
- Check Zammad for new Grafana alert tickets every 30 seconds
- Automatically process new tickets
- Create issues in Azure DevOps
- Update Zammad tickets with ADO links
- Run continuously until stopped (Ctrl+C)

### Option 3: List Available Tickets

```bash
python list_zammad_tickets.py
```

### Option 4: Check ADO Work Item Types

```bash
python check_ado_workitems.py
```

## 🎓 Context Studio Integration

This project uses **IBM ICA Context Studio** for:

### Knowledge Graph Schema:
- **Nodes:** Ticket, Log, Bug, Playbook
- **Relationships:** 
  - Ticket → HAS_LOGS → Log
  - Ticket → HAS_PLAYBOOK → Playbook
  - Ticket → CREATES_BUG → Bug
  - Bug → RELATED_TO → Ticket

### MCP Server:
- Exposes knowledge graph to Bob agent
- Provides context for intelligent decision-making
- Tracks workflow relationships

### GitHub Connector:
- Context Studio connects to this repository
- Bob accesses automation code via MCP
- Enables automatic execution of monitoring script

## 🤖 Bob Agent Configuration

Bob (the AI agent) is configured to:
1. Connect to Context Studio MCP server
2. Access automation code from this GitHub repository
3. Execute `monitor_tickets.py` continuously
4. Process new tickets automatically
5. Log all activities to Context Studio knowledge graph

## 📝 Features

✅ **Automatic ticket detection** - Monitors Zammad every 30 seconds
✅ **Log aggregation** - Fetches error logs from Loki
✅ **Issue creation** - Creates detailed issues in Azure DevOps
✅ **Ticket updates** - Updates Zammad with ADO links
✅ **Knowledge tracking** - Maintains relationships in Context Studio
✅ **Error handling** - Continues running even if services are unavailable
✅ **Severity-based processing** - Handles critical alerts appropriately

## 🔐 Security Notes

- **Never commit sensitive tokens** to the repository
- Use environment variables for credentials in production
- Rotate API tokens regularly
- Use GitHub secrets for CI/CD workflows

## 📈 Monitoring

The automation provides detailed logging:
- Timestamp for each action
- Success/failure status
- Ticket processing details
- Error messages and stack traces

## 🎯 Bobathon Challenge

This solution demonstrates:
- ✅ Multi-system integration (5 systems)
- ✅ Knowledge graph modeling
- ✅ MCP protocol implementation
- ✅ AI agent automation
- ✅ Production-ready code
- ✅ Complete documentation

## 📝 License

MIT License

## 👤 Author

**Azaz Shaik**
- GitHub: [@Ajaz8328](https://github.com/Ajaz8328)
- Created for Bobathon Challenge 2026

## 🙏 Acknowledgments

- IBM ICA Context Studio team
- Bobathon Challenge organizers
- Open source community

---

**Made with ❤️ for Bobathon Challenge 2026**