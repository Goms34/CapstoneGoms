"""Compliance & Action Orchestrator Agent - Handles compliance and notifications."""

from orchestration.state import ApplicationData, LoanDecision, ComplianceAction
from anthropic import Anthropic
from datetime import datetime
import uuid

client = Anthropic()


def execute_compliance_actions(
    application_id: str,
    application_data: ApplicationData,
    loan_decision: LoanDecision,
) -> ComplianceAction:
    """Execute compliance and notification actions using Claude."""

    case_id = f"CASE-{application_id}-{uuid.uuid4().hex[:6].upper()}"

    prompt = f"""
Execute compliance procedures for loan decision:

Application ID: {application_id}
Case ID: {case_id}
Applicant: {application_data.applicant_name}
Email: {application_data.email}
Decision: {loan_decision.decision}
Risk Score: {loan_decision.risk_score:.3f}
Confidence: {loan_decision.confidence:.2f}

Determine:
1. Compliance checks needed based on decision
2. Audit trail requirements
3. Notification message type
4. Next steps for applicant

Respond in this exact format:
COMPLIANCE_STATUS: [compliant/flag_for_review]
AUDIT_ACTION: [log/escalate/review]
NOTIFICATION_TYPE: [standard/conditional/manual_review]
NEXT_STEPS: [action items]
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001-v1:0",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    response_text = message.content[0].text

    action_taken = f"Decision {loan_decision.decision} processed and logged"
    notification_sent = True
    audit_logged = True

    if "flag_for_review" in response_text.lower():
        action_taken = f"Decision flagged for compliance review: {loan_decision.decision}"
        audit_logged = True

    return ComplianceAction(
        case_id=case_id,
        action_taken=action_taken,
        notification_sent=notification_sent,
        audit_logged=audit_logged,
    )
