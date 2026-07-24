"""Notification System MCP Server - Handles notifications and audit logging."""

from mcp.server.fastmcp import FastMCP
from datetime import datetime

server = FastMCP("NotificationSystem")

AUDIT_LOG = []
NOTIFICATIONS = {}


@server.tool()
def log_decision(
    application_id: str, decision: str, risk_score: float, confidence: float
) -> dict:
    """Log application decision to audit trail."""

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "application_id": application_id,
        "decision": decision,
        "risk_score": risk_score,
        "confidence": confidence,
        "status": "logged",
    }

    AUDIT_LOG.append(log_entry)

    return {
        "status": "success",
        "log_id": len(AUDIT_LOG),
        "entry": log_entry,
    }


@server.tool()
def send_notification(
    application_id: str, applicant_email: str, decision: str, case_id: str
) -> dict:
    """Send notification to applicant about decision."""

    notification = {
        "notification_id": len(NOTIFICATIONS) + 1,
        "application_id": application_id,
        "recipient": applicant_email,
        "decision": decision,
        "case_id": case_id,
        "sent_at": datetime.utcnow().isoformat(),
        "channel": "email",
        "status": "sent",
    }

    NOTIFICATIONS[application_id] = notification

    return {
        "status": "success",
        "notification": notification,
    }


@server.tool()
def create_case(application_id: str, decision: str, risk_score: float) -> dict:
    """Create a case record for the application."""

    case_id = f"CASE-{application_id}-{int(datetime.utcnow().timestamp())}"

    case_record = {
        "case_id": case_id,
        "application_id": application_id,
        "decision": decision,
        "risk_score": risk_score,
        "created_at": datetime.utcnow().isoformat(),
        "status": "created",
    }

    return {
        "status": "success",
        "case": case_record,
    }


@server.tool()
def get_audit_log(application_id: str = None) -> dict:
    """Retrieve audit log entries."""

    if application_id:
        entries = [e for e in AUDIT_LOG if e["application_id"] == application_id]
    else:
        entries = AUDIT_LOG

    return {
        "total_entries": len(entries),
        "entries": entries,
    }


@server.tool()
def get_notification_status(application_id: str) -> dict:
    """Get notification status for application."""

    if application_id in NOTIFICATIONS:
        return {
            "status": "found",
            "notification": NOTIFICATIONS[application_id],
        }

    return {
        "status": "not_found",
        "message": f"No notification found for {application_id}",
    }


if __name__ == "__main__":
    server.run()
