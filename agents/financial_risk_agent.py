"""Financial Risk Agent - Analyzes financial risk factors."""

from orchestration.state import ApplicationData, RiskAnalysis
from anthropic import Anthropic

client = Anthropic()


def analyze_financial_risk(application_data: ApplicationData) -> RiskAnalysis:
    """Analyze financial risk using Claude."""

    monthly_income = application_data.annual_income / 12
    monthly_liability = application_data.existing_liabilities / 12
    dti_ratio = monthly_liability / monthly_income if monthly_income > 0 else 1.0

    if dti_ratio < 0.36:
        dti_risk = 0.2
    elif dti_ratio < 0.43:
        dti_risk = 0.5
    else:
        dti_risk = 0.8

    if application_data.credit_score < 580:
        credit_risk = 0.9
    elif application_data.credit_score < 670:
        credit_risk = 0.6
    elif application_data.credit_score < 740:
        credit_risk = 0.3
    else:
        credit_risk = 0.1

    loan_amount_valid = application_data.loan_amount <= (application_data.annual_income * 5)

    prompt = f"""
Analyze the financial risk for this applicant:

Financial Information:
- Annual Income: ${application_data.annual_income:,.2f}
- Monthly Income: ${monthly_income:,.2f}
- Existing Liabilities: ${application_data.existing_liabilities:,.2f}
- Debt-to-Income Ratio: {dti_ratio:.2%}
- Credit Score: {application_data.credit_score}
- Loan Amount Requested: ${application_data.loan_amount:,.2f}
- Loan Tenure: {application_data.loan_tenure_months} months
- Loan-to-Income Multiple: {application_data.loan_amount / application_data.annual_income:.2f}x

Risk Assessment:
- DTI Risk Level: {"Low" if dti_ratio < 0.36 else "Moderate" if dti_ratio < 0.43 else "High"}
- Credit Risk Level: {"High" if application_data.credit_score < 580 else "Fair" if application_data.credit_score < 670 else "Good" if application_data.credit_score < 740 else "Excellent"}
- Loan Amount: {"Valid" if loan_amount_valid else "EXCESSIVE"}

Identify any financial anomalies or concerns.

Respond in this exact format:
DTI_RISK: [number 0-1]
CREDIT_RISK: [number 0-1]
ANOMALIES: [comma-separated list or "none"]
SUMMARY: [brief summary]
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

    anomalies = []
    if not loan_amount_valid:
        anomalies.append("Loan amount exceeds 5x annual income")
    if dti_ratio > 0.43:
        anomalies.append("High debt-to-income ratio")
    if application_data.credit_score < 600:
        anomalies.append("Low credit score")

    lines = response_text.split("\n")
    for line in lines:
        if line.startswith("ANOMALIES:"):
            anomaly_text = line.split(":", 1)[1].strip()
            if anomaly_text.lower() != "none":
                additional = [a.strip() for a in anomaly_text.split(",")]
                anomalies.extend(additional)

    return RiskAnalysis(
        dti_ratio=dti_ratio,
        dti_risk=dti_risk,
        credit_risk=credit_risk,
        loan_amount_valid=loan_amount_valid,
        anomalies=anomalies,
        anomalies_count=len(anomalies),
        analysis_notes=f"DTI: {dti_ratio:.2%}, Credit: {application_data.credit_score}",
    )
