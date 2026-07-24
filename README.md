# Loan Approval System - Multi-Agent Agentic AI

A production-ready system for automating loan approvals using domain-specific AI agents coordinated through LangGraph.

## Architecture

### Components
1. **Presentation Layer**: Streamlit-based chatbot UI
2. **Microservice Layer**: FastAPI REST endpoints
3. **Orchestration Layer**: LangGraph workflow engine
4. **Agent Layer**: 4 domain-specific agents
5. **Communication Layer**: MCP servers for standardized communication

### Agents
- **Applicant Profile Agent**: Analyzes applicant credentials, income stability, employment risk
- **Financial Risk Agent**: Calculates debt-to-income ratio, credit risk, detects anomalies
- **Loan Decision Agent**: Synthesizes all inputs into Approve/Reject/Manual Review
- **Compliance & Action Agent**: Routes decisions, sends notifications, maintains audit trail

## Setup

### Prerequisites
- Python 3.10+
- Anthropic API key

### Installation
```bash
pip install -e .
```

### Environment Setup
```bash
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

## Running the System

### Start MCP Servers
```bash
python mcp_servers/applicant_db.py
python mcp_servers/risk_rules_db.py
python mcp_servers/decision_synthesis.py
python mcp_servers/notification_system.py
```

### Start FastAPI Microservice
```bash
uvicorn api.main:app --reload
```

### Start Streamlit UI
```bash
streamlit run ui/app.py
```

## API Endpoints

- `POST /api/applications` - Submit loan application
- `GET /api/applications/{app_id}` - Get application status
- `GET /api/applications/{app_id}/decision` - Get decision with reasoning

## Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Manual Testing
1. Open Streamlit UI (typically `http://localhost:8501`)
2. Fill out loan application form
3. Submit and view decision

## Approval Criteria

- **DTI < 36%**: Low risk
- **Credit Score >= 670**: Good credit
- **Loan Amount <= 5x Annual Income**: Reasonable loan size
- **Combined Score**: Determines Approve/Reject/Manual Review

## Project Structure

```
loan-approval-system/
├── api/                    # FastAPI microservice
├── agents/                 # Agent implementations
├── mcp_servers/            # MCP server implementations
├── orchestration/          # LangGraph workflow
├── ui/                     # Streamlit UI
├── tests/                  # Test suite
├── docs/                   # Documentation
└── pyproject.toml         # Project configuration
```
