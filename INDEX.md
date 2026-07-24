# Loan Approval System - Complete Index

## 📚 Documentation (Start Here!)

### For Getting Started
1. **[README.md](README.md)** - Project overview, features, and structure
2. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup and first run
3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - What was built, features, and next steps

### For Understanding
4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Deep technical architecture, agents, data flow
5. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment, scaling, monitoring

## 🎯 Quick Links by Task

### I want to...

**Run the system locally**
→ Follow [QUICKSTART.md](QUICKSTART.md)

**Understand how it works**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md)

**Deploy to production**
→ Follow [DEPLOYMENT.md](DEPLOYMENT.md)

**Modify loan approval rules**
→ Edit `agents/loan_decision_agent.py` (Decision Agent)
→ Edit `agents/financial_risk_agent.py` (Financial Risk Agent)

**Add a new agent**
→ Create `agents/my_agent.py`
→ Add node to `orchestration/workflow.py`

**Integrate with external systems**
→ Review MCP servers in `mcp_servers/` directory
→ Create new MCP server following existing patterns

**See code examples**
→ Check `test_system.py` for agent usage
→ Review `ui/app.py` for UI patterns
→ Look at `api/main.py` for API endpoint patterns

**Run tests**
→ `pytest tests/` (test suite ready)
→ `python test_system.py` (component tests)

## 📂 Codebase Structure

```
api/                    ← FastAPI microservice
├── main.py            ← REST endpoints
├── models.py          ← Pydantic schemas
└── database.py        ← Data storage

agents/                 ← AI agents (Claude-powered)
├── applicant_profile_agent.py
├── financial_risk_agent.py
├── loan_decision_agent.py
└── compliance_agent.py

orchestration/          ← LangGraph workflow
├── workflow.py        ← Orchestration engine
└── state.py           ← State schema

ui/                     ← Streamlit web interface
└── app.py             ← User interface

mcp_servers/            ← Optional MCP integrations
├── applicant_db.py
├── risk_rules_db.py
├── decision_synthesis.py
└── notification_system.py

tests/                  ← Test suite (ready to extend)
├── test_api.py
├── test_workflow.py
└── test_agents.py

docs/                   ← Documentation directory
```

## 🔧 Configuration Files

- **pyproject.toml** - Project dependencies and metadata
- **.env** - Environment variables (API key, ports)
- **run_system.sh** - System startup script
- **test_system.py** - Integration test suite

## 🚀 Common Commands

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn streamlit anthropic pydantic httpx langgraph langchain
export ANTHROPIC_API_KEY=your_key_here
```

### Run
```bash
# Terminal 1: API
python -m uvicorn api.main:app --reload --port 8000

# Terminal 2: UI
streamlit run ui/app.py
```

### Test
```bash
python test_system.py
pytest tests/ -v
```

### Deploy
```bash
docker build -t loan-system .
docker run -e ANTHROPIC_API_KEY=key -p 8000:8000 loan-system
```

## 📊 System Workflow

```
User Input (Streamlit)
         ↓
Submit Application (FastAPI)
         ↓
Background Processing (LangGraph)
         ├── Validate Application
         ├── Profile Agent (Claude)
         ├── Risk Agent (Claude)
         ├── Decision Agent (Claude)
         └── Compliance Agent (Claude)
         ↓
Store Decision (Database)
         ↓
Display to User (Streamlit)
```

## 🎓 Architecture Overview

- **Layer 1 (UI)**: Streamlit web interface
- **Layer 2 (API)**: FastAPI REST microservice
- **Layer 3 (Orchestration)**: LangGraph state machine
- **Layer 4 (Agents)**: 4 domain-specific AI agents
- **Layer 5 (Communication)**: Mock MCP servers

## 🤖 The 4 Agents

1. **Applicant Profile Agent** - Analyzes income stability, employment risk
2. **Financial Risk Agent** - Calculates DTI, credit risk, anomaly detection
3. **Loan Decision Agent** - Synthesizes all inputs → Decision
4. **Compliance Agent** - Logs decisions, creates cases, notifications

## 📈 Decision Logic

```
Risk Scores (0-1):
├── Employment Risk (15%)
├── Income Stability (20%)
├── Credit Risk (35%)
├── DTI Risk (25%)
└── Loan Amount (5%)
    ↓
    Combined Risk Score
    ↓
    Decision Rules:
    • < 0.30 → Approve
    • 0.30-0.50 → Approve
    • 0.50-0.70 → Manual Review
    • > 0.70 → Reject
```

## 🔗 Key Technologies

| Component | Technology | Why |
|-----------|-----------|-----|
| UI | Streamlit | Fast development, interactive |
| API | FastAPI | Modern, async, fast |
| Orchestration | LangGraph | State management, workflows |
| AI | Claude API | Superior reasoning |
| Validation | Pydantic | Type-safe, validation |
| Async | asyncio | Non-blocking processing |

## 🎯 Features Checklist

- ✅ 4 domain-specific AI agents
- ✅ LangGraph orchestration
- ✅ FastAPI REST endpoints
- ✅ Streamlit web UI
- ✅ Async processing
- ✅ Decision explanations
- ✅ Risk scoring
- ✅ Compliance logging
- ✅ Error handling
- ✅ Extensible design
- ✅ Production patterns
- ✅ Comprehensive docs

## 📞 Getting Help

1. **Installation Issues** → [QUICKSTART.md](QUICKSTART.md)
2. **How it works** → [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Production setup** → [DEPLOYMENT.md](DEPLOYMENT.md)
4. **Code examples** → `test_system.py`, `ui/app.py`, `api/main.py`
5. **API reference** → Read docstrings in `api/main.py`

## 🚀 Next Steps

1. **Read** [QUICKSTART.md](QUICKSTART.md) to get running
2. **Explore** the codebase in your editor
3. **Run** `python -m uvicorn api.main:app --reload` 
4. **Open** Streamlit UI at `localhost:8501`
5. **Submit** a test application
6. **View** the decision and reasoning

## 📋 File Descriptions

### Entry Points
- `api/main.py` - Start here to understand API structure
- `ui/app.py` - Start here to understand UI
- `orchestration/workflow.py` - Start here to understand orchestration
- `agents/loan_decision_agent.py` - Start here to understand agents

### Reference
- `test_system.py` - See how agents are called
- `api/models.py` - See all data types
- `ARCHITECTURE.md` - See design patterns

---

**Ready?** Start with [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup!
