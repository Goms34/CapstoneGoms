"""Decision Synthesis MCP Server - Provides decision logic and thresholds."""

from mcp.server.fastmcp import FastMCP

server = FastMCP("DecisionSynthesis")


@server.tool()
def synthesize_decision(
    applicant_id: str,
    employment_risk: float,
    income_stability: float,
    credit_risk: float,
    dti_risk: float,
    loan_amount_valid: bool,
    anomalies_count: int,
) -> dict:
    """Synthesize all risk factors into a decision."""

    combined_risk_score = (
        employment_risk * 0.15
        + (1 - income_stability) * 0.2
        + credit_risk * 0.35
        + dti_risk * 0.25
        + (0.5 if not loan_amount_valid else 0) * 0.05
    )

    anomaly_penalty = min(anomalies_count * 0.15, 0.5)
    final_risk_score = min(combined_risk_score + anomaly_penalty, 1.0)

    if final_risk_score < 0.3:
        decision = "Approve"
        confidence = 0.95
        rationale = "Low risk profile with stable income and good credit."
    elif final_risk_score < 0.5:
        decision = "Approve"
        confidence = 0.75
        rationale = "Acceptable risk with some moderate concerns."
    elif final_risk_score < 0.7:
        decision = "Manual Review"
        confidence = 0.65
        rationale = "Mixed signals require human review."
    else:
        decision = "Reject"
        confidence = 0.85
        rationale = "High risk profile based on multiple factors."

    return {
        "applicant_id": applicant_id,
        "decision": decision,
        "risk_score": round(final_risk_score, 3),
        "confidence": confidence,
        "rationale": rationale,
        "component_scores": {
            "employment_risk": employment_risk,
            "income_stability_gap": 1 - income_stability,
            "credit_risk": credit_risk,
            "dti_risk": dti_risk,
            "loan_amount_risk": 0 if loan_amount_valid else 0.5,
            "anomaly_penalty": anomaly_penalty,
        },
    }


@server.tool()
def get_decision_factors(risk_score: float) -> dict:
    """Get key decision factors based on risk score."""

    if risk_score < 0.3:
        primary_factor = "Strong financial profile"
        secondary_factors = ["Good credit score", "Stable income", "Low debt burden"]
    elif risk_score < 0.5:
        primary_factor = "Acceptable financial profile"
        secondary_factors = ["Reasonable credit", "Adequate income", "Manageable debt"]
    elif risk_score < 0.7:
        primary_factor = "Mixed financial signals"
        secondary_factors = ["Some credit concerns", "Income variability", "High debt ratio"]
    else:
        primary_factor = "Concerning financial profile"
        secondary_factors = ["Low credit score", "Income instability", "High existing debt"]

    return {
        "risk_score": risk_score,
        "primary_factor": primary_factor,
        "secondary_factors": secondary_factors,
    }


@server.tool()
def calculate_approval_odds(risk_score: float) -> dict:
    """Calculate statistical approval likelihood."""

    approval_likelihood = max(0, min(1, 1 - risk_score))

    return {
        "risk_score": risk_score,
        "approval_likelihood": round(approval_likelihood, 2),
        "approval_percentage": round(approval_likelihood * 100, 1),
    }


if __name__ == "__main__":
    server.run()
