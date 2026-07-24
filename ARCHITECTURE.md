# Loan Approval System - Architecture Documentation

## System Overview

The **Intelligent Loan Approval System** is a production-ready multi-agent agentic AI application that automates loan approvals through coordinated domain-specific agents. The system provides explainable, auditable decisions at scale using Claude AI and LangGraph orchestration.

## Architecture Layers

### 1. Presentation Layer (Streamlit)
**File:** `ui/app.py`

The user-facing interface provides:
- 📝 **Application Submission**: Form for loan application entry
- 📊 **Status Tracking**: Real-time decision status  
- 📋 **Decision Display**: Risk scores, confidence, key factors, rationale
- 📱 **Application History**: View all submitted applications

**Key Features:**
- Multi-tab interface (New App, Check Status, All Applications)
- Streamlined form validation
- Real-time polling for decision updates
- Explainability display with risk visualization

### 2. API Layer (FastAPI)
**File:** `api/main.py`  
**Models:** `api/models.py`  
**Database:** `api/database.py`

RESTful microservice endpoints:
- `POST /api/applications` - Submit loan application (returns app_id)
- `GET /api/applications/{app_id}` - Get application status
- `GET /api/applications/{app_id}/decision` - Get decision with reasoning
- `GET /api/applications` - List all applications
- `GET /health` - Health check

**Response Models:**
- `LoanApplication`: Input validation using Pydantic
- `ApplicationResponse`: Submission confirmation  
- `DecisionResponse`: Full decision with audit trail
- `ApplicationStatus`: Current application state

**Database:**
- In-memory store (`applications_db`, `decisions_db`)
- Async application processing with background tasks
- Unique application ID generation

### 3. Orchestration Layer (LangGraph)
**Files:** `orchestration/workflow.py`, `orchestration/state.py`

LangGraph state machine coordinating the complete loan approval workflow:

```
Validate → Profile → Risk → Decision → Compliance → END
```

**Workflow Nodes:**
1. **validate** - Application data validation
2. **profile** - Applicant profile analysis
3. **risk** - Financial risk calculation
4. **decision** - Loan decision synthesis
5. **compliance** - Compliance actions & logging

**State Schema (`WorkflowState`):**
- `application_id`: Unique identifier
- `application_data`: Input loan application
- `profile_analysis`: Applicant profile results
- `risk_analysis`: Financial risk results
- `loan_decision`: Final decision + reasoning
- `compliance_action`: Case ID & audit trail
- `errors`: Error tracking
- `processing_log`: Execution trace

**Key Features:**
- Linear workflow with error handling
- Complete state persistence
- Processing log for debugging
- Graceful error propagation

### 4. Agent Layer (Domain-Specific Agents)
Each agent uses Claude AI for intelligent analysis and reasoning.

#### 4.1 Applicant Profile Agent
**File:** `agents/applicant_profile_agent.py`

**Responsibilities:**
- Analyze applicant credentials
- Calculate income stability score
- Assess employment risk
- Extract key profile insights

**Inputs:**
- Applicant name, age, education
- Employment type, years of employment
- Income (current and historical)
- Location

**Outputs:**
- `stability_score` (0-1): Income stability
- `employment_risk` (0-1): Employment risk level
- `income_stability` (0-1): Income consistency
- `employment_risk_level`: Low/Medium/High
- `analysis_notes`: Key observations

**Claude Prompts:**
- Income stability analysis based on employment history
- Employment type and tenure risk assessment
- Qualitative observations about applicant profile

#### 4.2 Financial Risk Agent
**File:** `agents/financial_risk_agent.py`

**Responsibilities:**
- Calculate debt-to-income ratio
- Assess credit risk
- Validate loan amount appropriateness
- Detect financial anomalies

**Inputs:**
- Annual income
- Existing liabilities
- Credit score
- Loan amount requested
- Employment tenure

**Outputs:**
- `dti_ratio` (0-1): Debt-to-income ratio
- `dti_risk` (0-1): DTI risk score
- `credit_risk` (0-1): Credit risk score
- `loan_amount_valid` (bool): Loan appropriateness
- `anomalies` (list): Detected anomalies
- `anomalies_count` (int): Number of anomalies

**Risk Scoring:**
- DTI < 36%: Low risk (0.2)
- DTI 36-43%: Moderate risk (0.5)
- DTI > 43%: High risk (0.8)
- Credit < 580: High risk (0.9)
- Credit 580-669: Fair risk (0.6)
- Credit 670-739: Good risk (0.3)
- Credit 740+: Excellent risk (0.1)

#### 4.3 Loan Decision Agent
**File:** `agents/loan_decision_agent.py`

**Responsibilities:**
- Synthesize profile and risk analysis
- Calculate combined risk score
- Make Approve/Reject/Manual Review decision
- Generate explainable reasoning

**Inputs:**
- Application data (income, credit, etc.)
- Profile analysis results
- Financial risk analysis results

**Outputs:**
- `decision`: Approve / Reject / Manual Review
- `risk_score` (0-1): Combined risk score
- `confidence` (0-1): Decision confidence
- `rationale`: Human-readable explanation
- `key_factors`: List of decision factors
- `reasoning_details`: Full Claude reasoning

**Decision Logic:**
- Risk < 0.30: **Approve** (95% confidence)
- Risk 0.30-0.50: **Approve** (75% confidence)
- Risk 0.50-0.70: **Manual Review** (65% confidence)
- Risk > 0.70: **Reject** (85% confidence)

**Risk Score Calculation:**
```
combined_risk = (
    employment_risk * 0.15 +
    (1 - income_stability) * 0.20 +
    credit_risk * 0.35 +
    dti_risk * 0.25 +
    loan_amount_penalty * 0.05
)

anomaly_penalty = min(anomalies_count * 0.15, 0.50)
final_risk = min(combined_risk + anomaly_penalty, 1.0)
```

**Weighting Rationale:**
- Credit Risk (35%): Strongest indicator of repayment capability
- DTI (25%): Capacity to make monthly payments
- Income Stability (20%): Consistency of cash flow
- Employment (15%): Job security
- Loan Amount (5%): Reasonableness of request size

#### 4.4 Compliance & Action Orchestrator Agent
**File:** `agents/compliance_agent.py`

**Responsibilities:**
- Create case records
- Log decisions to audit trail
- Generate notifications
- Ensure compliance procedures

**Inputs:**
- Application ID
- Applicant data
- Loan decision

**Outputs:**
- `case_id`: Unique case identifier
- `action_taken`: Compliance action description
- `notification_sent`: Notification status
- `audit_logged`: Audit trail status

**Compliance Features:**
- Case ID generation for tracking
- Audit trail logging
- Notification routing
- Compliance status tracking

### 5. Communication Layer (MCP Servers - Optional)
**Files:** `mcp_servers/*.py`

Mock MCP servers for future integration with external systems:

1. **ApplicantDB** - Applicant profile data
2. **RiskRulesDB** - Risk thresholds & rules
3. **DecisionSynthesis** - Decision logic
4. **NotificationSystem** - Audit logging

Current agents use direct Claude reasoning instead of MCP for simplicity.

## Data Flow

### Application Submission
```
User UI → FastAPI:POST /api/applications
→ Store in DB (pending status)
→ Background task: orchestration.process_application()
→ Return app_id to user
```

### Orchestration Workflow
```
LangGraph.invoke(WorkflowState)
├── validate: Check data validity
├── profile: Analyze applicant profile (Claude)
├── risk: Calculate financial risks (Claude)
├── decision: Make approval decision (Claude)
├── compliance: Log and notify (Claude)
└── Store decision in DB, update status to "completed"
```

### Decision Retrieval
```
User → FastAPI:GET /api/applications/{app_id}/decision
← Check decision_db
← Return decision with reasoning, confidence, case_id
```

## Key Technical Decisions

### 1. **LangGraph vs Direct Agent Orchestration**
- ✅ **Chosen:** LangGraph
- **Rationale:** Explicit workflow, easy visualization, state management, error handling
- **Alternative:** Direct async orchestration (less maintainable)

### 2. **Async Processing**
- ✅ **Chosen:** Background tasks with immediate app_id return
- **Rationale:** User doesn't wait for Claude reasoning (5-10 seconds)
- **Alternative:** Synchronous (blocks user, poor UX)

### 3. **In-Memory vs Persistent DB**
- ✅ **Chosen:** In-memory for demo, easy to swap to SQLite/PostgreSQL
- **Rationale:** Rapid development, demo-friendly
- **Production Path:** Add `api/db.py` with SQLAlchemy models

### 4. **Claude Model Selection**
- ✅ **Current:** Claude Haiku (fastest, cost-efficient)
- **Alternative:** Claude Sonnet 4.6 (higher reasoning but slower)
- **Alternative:** Claude Opus (most capable but expensive)

### 5. **Streamlit UI vs FastAPI+React**
- ✅ **Chosen:** Streamlit
- **Rationale:** Rapid development, easy iteration
- **Production Path:** React frontend + FastAPI backend

## Integration Points

### 1. Credit Bureau Integration
Replace mock score with real bureau API:
```python
# In financial_risk_agent.py
credit_score = real_credit_bureau.get_score(applicant_ssn)
```

### 2. Employment Verification
Replace mock employment data with real provider:
```python
# In applicant_profile_agent.py
employment_data = employment_verifier.verify(employer, applicant)
```

### 3. Compliance Systems
Replace notification logging with real systems:
```python
# In compliance_agent.py
audit_system.log_decision(decision, case_id)
notification_service.send_decision(applicant_email, decision)
```

### 4. Webhook Notifications
Add webhook support in FastAPI:
```python
@app.on_event("startup")
async def register_webhooks():
    await webhook_system.register_for_decisions()
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| API Response | < 100ms | FastAPI route, returns app_id immediately |
| Claude Reasoning | 5-10s | Per agent, 4 agents in sequence |
| Full Decision Latency | 20-40s | 4 agents + overhead |
| Memory Usage | < 100MB | In-memory store, no persistence |
| Concurrent Apps | Unlimited | Async task queue |
| API Throughput | 10+ req/sec | Depends on Claude API limits |

## Error Handling

### Application Validation
```python
# api/models.py - Pydantic validation
age: int = Field(..., ge=18, le=100)
annual_income: float = Field(..., gt=0)
credit_score: int = Field(..., ge=300, le=850)
```

### Workflow Errors
```python
# orchestration/workflow.py
if errors:
    state.errors.append(f"validation error: {e}")
    return state  # Continue to next node
```

### Agent Errors
```python
# agents/*.py
try:
    result = analyze_applicant_profile(app_data)
except Exception as e:
    state.errors.append(f"Profile analysis error: {e}")
    # Return safe defaults
```

## Scalability Path

### Phase 1: Current (Demo)
- Single FastAPI instance
- In-memory database
- Synchronous Streamlit UI

### Phase 2: Production
- FastAPI with Redis caching
- PostgreSQL persistence
- Async Streamlit callbacks
- Worker queue (Celery/RQ)

### Phase 3: Enterprise
- Kubernetes deployment
- Multi-region FastAPI
- ElasticSearch for audit logs
- Real-time WebSocket updates
- Compliance reporting dashboards

## Security Considerations

### Current Protections
- Input validation (Pydantic models)
- Application ID isolation
- CORS middleware

### Production Enhancements
- API authentication (OAuth2/JWT)
- Role-based access control
- Audit trail encryption
- Rate limiting
- Sensitive data masking

## Testing Strategy

### Unit Tests
- `tests/test_agents.py` - Individual agent behavior
- `tests/test_models.py` - Data validation
- `tests/test_workflow.py` - Orchestration logic

### Integration Tests
- `tests/test_api.py` - API endpoints
- `tests/test_e2e.py` - Full workflow

### Manual Testing
- Streamlit UI: Submit varied applications
- API curl: Direct endpoint testing
- Monitor logs: Error tracking

## Deployment

### Local Development
```bash
uvicorn api.main:app --reload --port 8000
streamlit run ui/app.py
```

### Docker (Future)
```dockerfile
FROM python:3.10
COPY . /app
WORKDIR /app
RUN pip install -e .
CMD ["uvicorn", "api.main:app"]
```

### Cloud (Vercel/Render)
```bash
# Vercel
vercel deploy

# Render
render deploy
```

## Monitoring & Observability

### Logging
- FastAPI logs all requests
- Agents log reasoning steps
- Workflow logs all transitions
- Errors logged with tracebacks

### Metrics to Track
- Average decision time
- Decision distribution (Approve/Reject/Review)
- Error rates by agent
- API latency percentiles

### Future: Observability Stack
- Prometheus metrics
- Grafana dashboards
- DataDog/Sentry integration
- OpenTelemetry tracing

## Maintenance

### Code Updates
- Update agent prompts in each `agents/*.py` file
- Modify decision logic in `loan_decision_agent.py`
- Add new endpoints in `api/main.py`
- Update Streamlit UI in `ui/app.py`

### Model Updates
- Change `model="claude-*"` parameter in agents
- Test with new model version
- Update QUICKSTART.md

### Threshold Changes
- Modify risk scoring in `financial_risk_agent.py`
- Update decision rules in `loan_decision_agent.py`
- Test with sample applications

## Conclusion

This architecture provides a scalable, maintainable foundation for intelligent loan approvals. The modular agent design, LangGraph orchestration, and clear data flow enable rapid iteration and future enhancements. Production deployment requires adding persistence, authentication, and monitoring.
