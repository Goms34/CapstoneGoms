"""Applicant Profile Agent - Analyzes applicant credentials and employment risk."""

from orchestration.state import ApplicationData, ProfileAnalysis
from anthropic import Anthropic

client = Anthropic()


def analyze_applicant_profile(application_data: ApplicationData) -> ProfileAnalysis:
    """Analyze applicant profile using Claude."""

    prompt = f"""
Analyze the following applicant profile and provide risk assessment:

Applicant Information:
- Name: {application_data.applicant_name}
- Age: {application_data.age}
- Employment Type: {application_data.employment_type}
- Years of Employment: {application_data.employment_years}
- Annual Income: ${application_data.annual_income:,.2f}
- Location: {application_data.location}

Based on this profile, please provide:
1. Income Stability Score (0-1, where 1 is most stable)
2. Employment Risk Score (0-1, where 0 is lowest risk)
3. Key observations about the applicant

Respond in this exact format:
STABILITY_SCORE: [number 0-1]
EMPLOYMENT_RISK: [number 0-1]
OBSERVATIONS: [brief observations]
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

    stability_score = 0.7
    employment_risk = 0.2
    observations = ""

    lines = response_text.split("\n")
    for line in lines:
        if line.startswith("STABILITY_SCORE:"):
            try:
                stability_score = float(line.split(":")[1].strip())
            except ValueError:
                pass
        elif line.startswith("EMPLOYMENT_RISK:"):
            try:
                employment_risk = float(line.split(":")[1].strip())
            except ValueError:
                pass
        elif line.startswith("OBSERVATIONS:"):
            observations = line.split(":", 1)[1].strip()

    income_stability = stability_score

    risk_level = (
        "low" if employment_risk < 0.33 else "medium" if employment_risk < 0.67 else "high"
    )

    return ProfileAnalysis(
        stability_score=stability_score,
        employment_risk=employment_risk,
        income_stability=income_stability,
        employment_risk_level=risk_level,
        analysis_notes=observations,
    )
