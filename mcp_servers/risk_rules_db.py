"""Risk Rules Database MCP Server - Provides risk thresholds and rules."""

from mcp.server.fastmcp import FastMCP

server = FastMCP("RiskRulesDB")

RISK_THRESHOLDS = {
    "credit_score": {
        "high_risk": 580,
        "fair": 669,
        "good": 739,
        "excellent": 740,
    },
    "debt_to_income": {
        "low_risk": 0.36,
        "moderate_risk": 0.43,
        "high_risk": 0.43,
    },
    "income_multiple": {
        "max_loan_multiple": 5.0,
    },
    "employment": {
        "min_years_full_time": 2,
        "min_years_self_employed": 3,
    },
}


@server.tool()
def get_credit_score_risk(credit_score: int) -> dict:
    """Determine credit score risk level."""
    if credit_score < 580:
        risk_level = "high"
        risk_score = 0.9
    elif credit_score < 670:
        risk_level = "fair"
        risk_score = 0.6
    elif credit_score < 740:
        risk_level = "good"
        risk_score = 0.3
    else:
        risk_level = "excellent"
        risk_score = 0.1

    return {
        "credit_score": credit_score,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "thresholds": RISK_THRESHOLDS["credit_score"],
    }


@server.tool()
def calculate_debt_to_income_risk(monthly_income: float, monthly_debt: float) -> dict:
    """Calculate debt-to-income ratio and risk level."""
    if monthly_income == 0:
        return {"error": "Monthly income cannot be zero"}

    dti_ratio = monthly_debt / monthly_income

    if dti_ratio < 0.36:
        risk_level = "low"
        risk_score = 0.2
    elif dti_ratio < 0.43:
        risk_level = "moderate"
        risk_score = 0.5
    else:
        risk_level = "high"
        risk_score = 0.8

    return {
        "dti_ratio": round(dti_ratio, 4),
        "risk_level": risk_level,
        "risk_score": risk_score,
        "monthly_income": monthly_income,
        "monthly_debt": monthly_debt,
        "thresholds": RISK_THRESHOLDS["debt_to_income"],
    }


@server.tool()
def validate_loan_amount(annual_income: float, loan_amount: float) -> dict:
    """Validate loan amount against income multiples."""
    max_loan = annual_income * RISK_THRESHOLDS["income_multiple"]["max_loan_multiple"]
    is_valid = loan_amount <= max_loan

    return {
        "annual_income": annual_income,
        "loan_amount": loan_amount,
        "max_allowed": max_loan,
        "is_valid": is_valid,
        "ratio": round(loan_amount / annual_income, 2),
        "max_multiple": RISK_THRESHOLDS["income_multiple"]["max_loan_multiple"],
    }


@server.tool()
def detect_anomalies(
    credit_score: int, annual_income: float, existing_liabilities: float, loan_amount: float
) -> dict:
    """Detect financial anomalies."""
    anomalies = []

    if credit_score < 600:
        anomalies.append("Very low credit score")

    if existing_liabilities > annual_income * 0.5:
        anomalies.append("High existing liabilities relative to income")

    if loan_amount > annual_income * 5:
        anomalies.append("Loan amount exceeds 5x annual income")

    if annual_income < 30000:
        anomalies.append("Low annual income")

    return {
        "anomalies_detected": len(anomalies) > 0,
        "anomalies": anomalies,
        "anomaly_count": len(anomalies),
    }


if __name__ == "__main__":
    server.run()
