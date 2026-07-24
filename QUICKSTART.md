# Quick Start Guide - Loan Approval System

## Prerequisites

- Python 3.10+
- Anthropic API Key (set `ANTHROPIC_API_KEY` environment variable)

## Setup (One-Time)

```bash
# Navigate to project directory
cd /Software/langenv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn streamlit anthropic pydantic python-dotenv httpx langgraph langchain

# Set your API key
export ANTHROPIC_API_KEY=your_api_key_here
```

## Running the System

### Option 1: Run Everything (Recommended for Testing)

Open three terminals and run these commands:

**Terminal 1 - FastAPI Server:**
```bash
cd /Software/langenv
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Streamlit UI:**
```bash
cd /Software/langenv
source venv/bin/activate
streamlit run ui/app.py
```

The Streamlit app will open at `http://localhost:8501`

### Option 2: Quick Test (API Only)

```bash
cd /Software/langenv
source venv/bin/activate
python -m uvicorn api.main:app --port 8000 &

# Submit a test application
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "APP001",
    "applicant_name": "John Smith",
    "age": 35,
    "annual_income": 85000,
    "employment_type": "Full-Time",
    "employment_years": 5,
    "existing_liabilities": 15000,
    "credit_score": 720,
    "loan_amount": 50000,
    "loan_tenure_months": 60,
    "location": "New York",
    "email": "john@example.com"
  }'

# Check status
curl http://localhost:8000/api/applications

# Get decision (after ~5-10 seconds)
curl http://localhost:8000/api/applications/{app_id}/decision
```

## System Architecture

### Layers

1. **Presentation Layer** (Streamlit)
   - User-friendly interface for submitting applications
   - Real-time status tracking
   - Decision visualization with reasoning

2. **API Layer** (FastAPI)
   - `POST /api/applications` - Submit application
   - `GET /api/applications/{app_id}` - Get status
   - `GET /api/applications/{app_id}/decision` - Get decision
   - `GET /api/applications` - List all applications

3. **Orchestration Layer** (LangGraph)
   - Workflow coordination across agents
   - State management
   - Error handling

4. **Agent Layer** (Claude AI)
   - **Applicant Profile Agent**: Income stability, employment risk analysis
   - **Financial Risk Agent**: DTI ratio, credit risk, anomaly detection
   - **Loan Decision Agent**: Synthesizes all inputs → Approve/Reject/Manual Review
   - **Compliance Agent**: Logging, notifications, case management

### Approval Decision Logic

**Risk Score Calculation:**
- Employment Risk: 15% weight
- Income Stability: 20% weight
- Credit Risk: 35% weight
- DTI Risk: 25% weight
- Loan Amount Validity: 5% weight

**Decision Rules:**
- Risk < 0.30: **Approve** (confidence 95%)
- Risk 0.30-0.50: **Approve** (confidence 75%, conditional)
- Risk 0.50-0.70: **Manual Review** (confidence 65%)
- Risk > 0.70: **Reject** (confidence 85%)

## Test Data

### Example 1: Strong Applicant (Expected: Approve)
```json
{
  "applicant_id": "APP001",
  "applicant_name": "John Smith",
  "age": 35,
  "annual_income": 85000,
  "employment_type": "Full-Time",
  "employment_years": 5,
  "existing_liabilities": 15000,
  "credit_score": 720,
  "loan_amount": 50000,
  "loan_tenure_months": 60,
  "location": "New York",
  "email": "john@example.com"
}
```

### Example 2: Borderline Applicant (Expected: Manual Review)
```json
{
  "applicant_id": "APP002",
  "applicant_name": "Jane Doe",
  "age": 28,
  "annual_income": 45000,
  "employment_type": "Contract",
  "employment_years": 1,
  "existing_liabilities": 25000,
  "credit_score": 620,
  "loan_amount": 40000,
  "loan_tenure_months": 48,
  "location": "California",
  "email": "jane@example.com"
}
```

### Example 3: High Risk (Expected: Reject)
```json
{
  "applicant_id": "APP003",
  "applicant_name": "Bob Johnson",
  "age": 50,
  "annual_income": 30000,
  "employment_type": "Part-Time",
  "employment_years": 0,
  "existing_liabilities": 60000,
  "credit_score": 550,
  "loan_amount": 100000,
  "loan_tenure_months": 120,
  "location": "Texas",
  "email": "bob@example.com"
}
```

## Features

✅ **Multi-Agent Architecture**: Domain-specific agents collaborate through orchestration
✅ **Explainable Decisions**: See reasoning, risk factors, and confidence scores
✅ **Async Processing**: Applications processed in background
✅ **Real-time Status Tracking**: Check decision status at any time
✅ **Audit Trail**: Compliance logging for all decisions
✅ **Web UI**: Streamlit-based user interface
✅ **REST API**: FastAPI endpoints for integration
✅ **Production-Ready**: Error handling, logging, validation

## Troubleshooting

### "Connection refused" error
Make sure FastAPI is running on port 8000:
```bash
python -m uvicorn api.main:app --reload --port 8000
```

### "ANTHROPIC_API_KEY not found"
Set your API key:
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

### Application processing takes long
Claude AI reasoning can take 5-10 seconds. Be patient or check status later.

### "Application not found"
Make sure you're using the correct application ID returned from submission.

## API Examples

### Submit Application
```bash
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d '{...json payload...}'

# Response:
{
  "application_id": "APP-12345678",
  "status": "submitted",
  "message": "Application APP-12345678 submitted successfully. Processing has started."
}
```

### Check Status
```bash
curl http://localhost:8000/api/applications/APP-12345678

# Response:
{
  "application_id": "APP-12345678",
  "applicant_id": "APP001",
  "status": "completed",
  "submitted_at": "2024-01-15T10:30:00",
  "decision": "Approve"
}
```

### Get Decision with Details
```bash
curl http://localhost:8000/api/applications/APP-12345678/decision

# Response:
{
  "application_id": "APP-12345678",
  "decision": {
    "decision": "Approve",
    "risk_score": 0.32,
    "confidence": 0.75,
    "rationale": "Acceptable risk with reasonable financial metrics.",
    "key_factors": [
      "Employment Risk: low",
      "Credit Score: 720",
      "DTI Ratio: Low"
    ],
    "case_id": "CASE-APP-12345678-ABC123"
  },
  "audit_trail": {
    "processed_at": "2024-01-15T10:30:15",
    "status": "completed"
  }
}
```

## Next Steps

- Customize approval thresholds in `agents/loan_decision_agent.py`
- Add database persistence (SQLite/PostgreSQL)
- Integrate with external credit bureaus
- Add webhook notifications
- Implement advanced ML models for risk scoring
- Add compliance reports and dashboards

## Support

For issues or questions, check the system logs in the terminal outputs.
