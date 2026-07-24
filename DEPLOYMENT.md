# Deployment Guide - Loan Approval System

## Quick Start (5 minutes)

### 1. Prerequisites
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Set API key
export ANTHROPIC_API_KEY=your_api_key_here

# Navigate to project
cd /Software/langenv
```

### 2. Setup Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn streamlit anthropic pydantic python-dotenv httpx langgraph langchain
```

### 3. Run the System

**Terminal 1 - FastAPI Server:**
```bash
source venv/bin/activate
python -m uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Streamlit UI:**
```bash
source venv/bin/activate
streamlit run ui/app.py
```

Visit: `http://localhost:8501`

## System Verification

### Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Submit Test Application
```bash
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST001",
    "applicant_name": "Test Applicant",
    "age": 35,
    "annual_income": 85000,
    "employment_type": "Full-Time",
    "employment_years": 5,
    "existing_liabilities": 15000,
    "credit_score": 720,
    "loan_amount": 50000,
    "loan_tenure_months": 60,
    "location": "New York",
    "email": "test@example.com"
  }'
```

Response includes `application_id`. Use it to check status:

```bash
curl http://localhost:8000/api/applications/{app_id}
curl http://localhost:8000/api/applications/{app_id}/decision
```

## Production Deployment

### Option 1: Docker Containerization

**Create Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY . .

ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t loan-approval-system .
docker run -e ANTHROPIC_API_KEY=your_key -p 8000:8000 loan-approval-system
```

### Option 2: Cloud Deployment

#### Render.com (Recommended - Free Tier Available)
```bash
# 1. Create render.yaml
version: 1
services:
  - type: web
    name: loan-approval-api
    env: python
    buildCommand: pip install -e .
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port 8000
    envVars:
      - key: ANTHROPIC_API_KEY
        scope: build,runtime
        value: your_key_here
```

#### Vercel (For UI)
```bash
# Deploy Streamlit frontend separately
vercel env add ANTHROPIC_API_KEY your_key_here
vercel deploy
```

#### AWS Lambda + API Gateway
```python
# serverless.yml
service: loan-approval-system
provider:
  name: aws
  runtime: python3.10
  environment:
    ANTHROPIC_API_KEY: ${env:ANTHROPIC_API_KEY}
functions:
  api:
    handler: api.main.app
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

### Option 3: Heroku

```bash
# Create Procfile
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT

# Deploy
git push heroku main
heroku config:set ANTHROPIC_API_KEY=your_key_here
```

## Configuration

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
LOG_LEVEL=INFO
DATABASE_URL=postgresql://...  # For production
REDIS_URL=redis://...          # For caching
```

### Model Configuration
Edit agent files to change model:
```python
# agents/applicant_profile_agent.py
message = client.messages.create(
    model="claude-opus-4-5-20251101-v1:0",  # Change here
    max_tokens=500,
    messages=[...]
)
```

### Decision Thresholds
Edit decision logic:
```python
# agents/loan_decision_agent.py

# Modify these risk thresholds:
if final_risk_score < 0.25:  # Lower = stricter
    decision = "Approve"
elif final_risk_score < 0.55:  # Adjust threshold
    decision = "Approve"
```

## Database Setup (Production)

### PostgreSQL Migration
```python
# api/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)
```

### Redis Caching
```python
# Add to api/main.py
import redis

redis_client = redis.from_url(os.getenv("REDIS_URL"))

@app.get("/api/applications/{app_id}/cached")
def get_cached_decision(app_id: str):
    cached = redis_client.get(f"decision:{app_id}")
    if cached:
        return json.loads(cached)
    # Fetch from DB...
```

## Monitoring Setup

### Logging (Production)
```python
# Add to api/main.py
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "loan_system.log",
    maxBytes=10485760,  # 10MB
    backupCount=5
)
logging.getLogger().addHandler(handler)
```

### Error Tracking (Sentry)
```python
# Add to api/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()]
)
```

### Metrics (Prometheus)
```python
# Add to api/main.py
from prometheus_client import Counter, Histogram

decisions_counter = Counter(
    'loan_decisions_total',
    'Total loan decisions',
    ['decision_type']
)

processing_time = Histogram(
    'loan_processing_seconds',
    'Time to process loan application'
)
```

## Scaling

### Horizontal Scaling
```bash
# Multiple FastAPI instances behind load balancer
# Use environment-specific config

# nginx.conf
upstream loan_system {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://loan_system;
    }
}
```

### Worker Pool (Celery)
```python
# For background processing
from celery import Celery

celery_app = Celery(
    'loan_system',
    broker='redis://localhost',
    backend='redis://localhost'
)

@celery_app.task
def process_application_async(app_id, app_data):
    return process_application(app_id, app_data)
```

## Security Hardening

### 1. API Authentication
```python
# Add to api/main.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/api/applications")
async def submit_application(
    application: LoanApplication,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify JWT token
    verify_token(credentials.credentials)
    # Continue...
```

### 2. Rate Limiting
```python
# Add to api/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/applications")
@limiter.limit("10/minute")
async def submit_application(...):
    pass
```

### 3. Input Sanitization
```python
# Already done with Pydantic validation
# Add additional sanitization if needed:
import bleach

def sanitize_text(text: str) -> str:
    return bleach.clean(text, tags=[], strip=True)
```

### 4. HTTPS/TLS
```bash
# Use reverse proxy with SSL
# Example: Nginx with Let's Encrypt

server {
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/domain/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domain/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

## Testing

### Unit Tests
```bash
pytest tests/test_models.py -v
pytest tests/test_agents.py -v
```

### Integration Tests
```bash
pytest tests/test_api.py -v
pytest tests/test_workflow.py -v
```

### Load Testing
```bash
# Using locust
pip install locust
locust -f tests/load_test.py --host=http://localhost:8000
```

### Manual Testing Checklist
- [ ] Approve good applicant (high income, good credit)
- [ ] Reject poor applicant (low income, bad credit)
- [ ] Manual review borderline applicant (mixed signals)
- [ ] Check application history page
- [ ] Verify decision reasoning matches inputs
- [ ] Test API with curl/Postman
- [ ] Monitor response times

## Troubleshooting

### API Won't Start
```bash
# Check port 8000 is available
lsof -i :8000

# Kill process on port 8000
kill -9 <PID>

# Start with different port
uvicorn api.main:app --port 8001
```

### Streamlit Connection Errors
```bash
# Check FastAPI is running
curl http://localhost:8000/health

# Update FASTAPI_URL in ui/app.py if needed
FASTAPI_URL = "http://your-api-domain.com"
```

### Slow Decision Making
- Current: 20-40 seconds per application
- Use Haiku model (faster) vs Opus (slower)
- Check Claude API quota

### Memory Issues
```bash
# Monitor memory usage
free -h

# Clear in-memory database if needed
# Add to api/database.py:
from api.database import clear_all
clear_all()
```

## Backup & Recovery

### Application Data
```bash
# Export all decisions to JSON
python -c "
from api.database import get_all_decisions
import json
with open('backup.json', 'w') as f:
    json.dump(get_all_decisions(), f)
"
```

### Database Backups
```bash
# PostgreSQL backup
pg_dump loan_db > backup.sql

# Restore
psql loan_db < backup.sql
```

## Performance Optimization

### Caching
```python
# Cache decision logic
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_decision_logic(risk_score: float):
    # Return cached decision
    pass
```

### Batch Processing
```python
# Process multiple applications at once
@app.post("/api/applications/batch")
async def batch_submit_applications(
    applications: List[LoanApplication]
):
    tasks = [
        process_application_async(app_id, app.dict())
        for app_id, app in applications
    ]
    results = await asyncio.gather(*tasks)
    return results
```

## Support & Maintenance

### Regular Tasks
- [ ] Monitor error logs weekly
- [ ] Check decision accuracy monthly
- [ ] Update thresholds quarterly
- [ ] Review security patches monthly
- [ ] Backup data daily

### Documentation
- Keep ARCHITECTURE.md updated
- Update decision logic documentation
- Document custom integrations
- Maintain runbooks for common issues

## Escalation Path

1. **Development**: Local testing → QA staging
2. **Staging**: Full testing, load testing
3. **Production**: Blue-green deployment
4. **Monitoring**: Alert on errors, anomalies
5. **Incident Response**: Rollback procedures

## Getting Help

- Check QUICKSTART.md for common issues
- Review ARCHITECTURE.md for design details
- Examine test suite (`tests/`) for examples
- Check logs: `loan_system.log`
- Claude API docs: https://docs.anthropic.com
- LangGraph docs: https://python.langchain.com/docs/langgraph

---

**Ready to deploy?** Follow Quick Start section above to get running in 5 minutes.
