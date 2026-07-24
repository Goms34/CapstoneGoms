"""In-memory database for application storage."""

from datetime import datetime
from typing import Dict, Optional
import uuid

applications_db: Dict[str, dict] = {}
decisions_db: Dict[str, dict] = {}


def create_application_id() -> str:
    """Generate unique application ID."""
    return f"APP-{uuid.uuid4().hex[:8].upper()}"


def store_application(application_data: dict) -> str:
    """Store application and return ID."""
    app_id = create_application_id()
    applications_db[app_id] = {
        "id": app_id,
        "data": application_data,
        "submitted_at": datetime.utcnow().isoformat(),
        "status": "pending",
    }
    return app_id


def get_application(app_id: str) -> Optional[dict]:
    """Retrieve application by ID."""
    return applications_db.get(app_id)


def update_application_status(app_id: str, status: str) -> bool:
    """Update application status."""
    if app_id in applications_db:
        applications_db[app_id]["status"] = status
        return True
    return False


def store_decision(app_id: str, decision: dict) -> bool:
    """Store decision for application."""
    if app_id in applications_db:
        decisions_db[app_id] = {
            "id": app_id,
            "decision": decision,
            "processed_at": datetime.utcnow().isoformat(),
        }
        applications_db[app_id]["status"] = "completed"
        return True
    return False


def get_decision(app_id: str) -> Optional[dict]:
    """Retrieve decision by application ID."""
    return decisions_db.get(app_id)


def get_all_applications() -> Dict[str, dict]:
    """Get all applications."""
    return applications_db


def get_all_decisions() -> Dict[str, dict]:
    """Get all decisions."""
    return decisions_db


def clear_all() -> None:
    """Clear all data (for testing)."""
    global applications_db, decisions_db
    applications_db.clear()
    decisions_db.clear()
