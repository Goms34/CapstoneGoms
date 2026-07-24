"""FastAPI microservice for loan application processing."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from typing import Optional

from api.models import LoanApplication, ApplicationResponse, DecisionResponse, Decision
from api.database import store_application, get_application, store_decision, get_decision
from orchestration.workflow import process_application

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Loan Approval System", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/applications", response_model=ApplicationResponse)
async def submit_application(application: LoanApplication) -> ApplicationResponse:
    """Submit a loan application."""
    try:
        app_data = application.model_dump()

        app_id = store_application(app_data)

        asyncio.create_task(process_application_async(app_id, app_data))

        return ApplicationResponse(
            application_id=app_id,
            status="submitted",
            message=f"Application {app_id} submitted successfully. Processing has started.",
        )

    except Exception as e:
        logger.error(f"Error submitting application: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def process_application_async(app_id: str, app_data: dict):
    """Process application asynchronously."""
    try:
        logger.info(f"Starting async processing for {app_id}")
        final_state = await process_application(app_id, app_data)

        decision_dict = {
            "decision": final_state.loan_decision.decision,
            "risk_score": final_state.loan_decision.risk_score,
            "confidence": final_state.loan_decision.confidence,
            "rationale": final_state.loan_decision.rationale,
            "key_factors": final_state.loan_decision.key_factors,
            "case_id": final_state.compliance_action.case_id,
        }

        store_decision(app_id, decision_dict)
        logger.info(f"Decision stored for {app_id}: {final_state.loan_decision.decision}")

    except Exception as e:
        logger.error(f"Error processing application {app_id}: {e}")


@app.get("/api/applications/{app_id}")
def get_application_status(app_id: str):
    """Get application status."""
    try:
        app = get_application(app_id)
        if not app:
            raise HTTPException(status_code=404, detail=f"Application {app_id} not found")

        decision = get_decision(app_id)

        return {
            "application_id": app_id,
            "applicant_id": app["data"].get("applicant_id"),
            "status": app["status"],
            "submitted_at": app["submitted_at"],
            "decision": decision["decision"] if decision else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/applications/{app_id}/decision", response_model=Optional[DecisionResponse])
def get_application_decision(app_id: str):
    """Get application decision with reasoning."""
    try:
        app = get_application(app_id)
        if not app:
            raise HTTPException(status_code=404, detail=f"Application {app_id} not found")

        decision_data = get_decision(app_id)
        if not decision_data:
            return {
                "application_id": app_id,
                "status": "pending",
                "message": "Decision is being processed",
            }

        decision = decision_data["decision"]

        return DecisionResponse(
            application_id=app_id,
            decision=Decision(
                decision=decision["decision"],
                risk_score=decision["risk_score"],
                confidence=decision["confidence"],
                rationale=decision["rationale"],
                key_factors=decision["key_factors"],
                case_id=decision.get("case_id"),
            ),
            audit_trail={
                "processed_at": decision_data["processed_at"],
                "status": "completed",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving decision: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/applications")
def list_applications():
    """List all applications."""
    from api.database import get_all_applications

    try:
        apps = get_all_applications()
        return {
            "total": len(apps),
            "applications": [
                {
                    "application_id": aid,
                    "applicant_id": a["data"].get("applicant_id"),
                    "status": a["status"],
                    "submitted_at": a["submitted_at"],
                }
                for aid, a in apps.items()
            ],
        }

    except Exception as e:
        logger.error(f"Error listing applications: {e}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
