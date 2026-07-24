"""Loan Decision Agent - Synthesizes analysis and makes approval decision."""

from orchestration.state import ApplicationData, ProfileAnalysis, RiskAnalysis, LoanDecision
from anthropic import Anthropic

client = Anthropic()


def make_loan_decision(
    application_data: ApplicationData,
    profile_analysis: ProfileAnalysis,
    risk_analysis: RiskAnalysis,
) -> LoanDecision:
    """Make loan decision using Claude."""

    combined_risk = (
        profile_analysis.employment_risk * 0.15
        + (1 - profile_analysis.income_stability) * 0.2
        + risk_analysis.credit_risk * 0.35
        + risk_analysis.dti_risk * 0.25
        + (0.5 if not risk_analysis.loan_amount_valid else 0) * 0.05
    )

    anomaly_penalty = min(risk_analysis.anomalies_count * 0.15, 0.5)
    final_risk_score = min(combined_risk + anomaly_penalty, 1.0)

    prompt = f"""
Based on comprehensive financial analysis, make a loan approval decision:

Applicant Summary:
- Annual Income: ${application_data.annual_income:,.2f}
- Credit Score: {application_data.credit_score}
- Employment: {application_data.employment_type} ({application_data.employment_years} years)
- Loan Amount: ${application_data.loan_amount:,.2f}

Risk Assessment:
- Employment Risk: {profile_analysis.employment_risk:.2f}
- Income Stability: {profile_analysis.income_stability:.2f}
- Credit Risk: {risk_analysis.credit_risk:.2f}
- DTI Risk: {risk_analysis.dti_risk:.2f}
- Combined Risk Score: {final_risk_score:.3f}
- Detected Anomalies: {len(risk_analysis.anomalies)} ({', '.join(risk_analysis.anomalies) if risk_analysis.anomalies else 'none'})

Decision Rules:
- Risk < 0.3: Approve
- Risk 0.3-0.5: Approve (conditional)
- Risk 0.5-0.7: Manual Review
- Risk > 0.7: Reject

Make a decision and explain the key factors.

Respond in this exact format:
DECISION: [Approve/Reject/Manual Review]
CONFIDENCE: [0-1 confidence score]
KEY_FACTORS: [3-5 bullet points explaining decision]
RATIONALE: [1-2 sentence explanation]
"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001-v1:0",
        max_tokens=600,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    response_text = message.content[0].text

    decision = "Manual Review"
    confidence = 0.5
    rationale = ""
    key_factors = []

    if final_risk_score < 0.3:
        decision = "Approve"
        confidence = 0.95
        rationale = "Low risk profile with stable income and good credit."
    elif final_risk_score < 0.5:
        decision = "Approve"
        confidence = 0.75
        rationale = "Acceptable risk with reasonable financial metrics."
    elif final_risk_score < 0.7:
        decision = "Manual Review"
        confidence = 0.65
        rationale = "Mixed signals require human review for final decision."
    else:
        decision = "Reject"
        confidence = 0.85
        rationale = "High risk profile based on multiple financial indicators."

    lines = response_text.split("\n")
    for line in lines:
        if line.startswith("DECISION:"):
            decision_text = line.split(":", 1)[1].strip()
            if any(d in decision_text for d in ["Approve", "Reject", "Manual"]):
                decision = decision_text
        elif line.startswith("CONFIDENCE:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("RATIONALE:"):
            rationale = line.split(":", 1)[1].strip()
        elif line.startswith("KEY_FACTORS:"):
            factors_text = line.split(":", 1)[1].strip()
            key_factors = [f.strip() for f in factors_text.split(",")]

    if not key_factors:
        key_factors = [
            f"Employment Risk: {profile_analysis.employment_risk_level}",
            f"Credit Score: {application_data.credit_score}",
            f"DTI Ratio: Low" if risk_analysis.dti_risk < 0.4 else f"DTI Ratio: High",
        ]

    return LoanDecision(
        decision=decision,
        risk_score=final_risk_score,
        confidence=confidence,
        rationale=rationale,
        key_factors=key_factors,
        reasoning_details=response_text,
    )
