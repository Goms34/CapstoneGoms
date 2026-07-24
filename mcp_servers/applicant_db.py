"""Applicant Database MCP Server - Provides applicant profile data."""

from mcp.server.fastmcp import FastMCP
import json

server = FastMCP("ApplicantDB")

APPLICANT_DATA = {
    "APP001": {
        "applicant_id": "APP001",
        "name": "John Smith",
        "age": 35,
        "employment_type": "Full-Time",
        "current_employer": "Tech Corp",
        "employment_years": 5,
        "annual_income": 85000,
        "income_history": [75000, 78000, 82000, 85000],
        "education": "Bachelor's",
        "phone": "555-1234",
        "email": "john@example.com",
        "existing_liabilities": 15000,
        "location": "New York",
    },
    "APP002": {
        "applicant_id": "APP002",
        "name": "Jane Doe",
        "age": 28,
        "employment_type": "Full-Time",
        "current_employer": "Finance Inc",
        "employment_years": 3,
        "annual_income": 65000,
        "income_history": [55000, 60000, 65000],
        "education": "Master's",
        "phone": "555-5678",
        "email": "jane@example.com",
        "existing_liabilities": 8000,
        "location": "California",
    },
    "APP003": {
        "applicant_id": "APP003",
        "name": "Bob Johnson",
        "age": 45,
        "employment_type": "Self-Employed",
        "current_employer": "Self",
        "employment_years": 10,
        "annual_income": 120000,
        "income_history": [100000, 95000, 120000, 110000],
        "education": "High School",
        "phone": "555-9999",
        "email": "bob@example.com",
        "existing_liabilities": 45000,
        "location": "Texas",
    },
}


@server.tool()
def get_applicant_profile(applicant_id: str) -> dict:
    """Fetch applicant profile information."""
    if applicant_id in APPLICANT_DATA:
        return APPLICANT_DATA[applicant_id]
    return {"error": f"Applicant {applicant_id} not found"}


@server.tool()
def calculate_income_stability(applicant_id: str) -> dict:
    """Calculate income stability score based on history."""
    if applicant_id not in APPLICANT_DATA:
        return {"error": f"Applicant {applicant_id} not found"}

    profile = APPLICANT_DATA[applicant_id]
    income_history = profile["income_history"]

    if len(income_history) < 2:
        return {"stability_score": 0.5, "status": "insufficient_data"}

    avg_income = sum(income_history) / len(income_history)
    variance = sum((x - avg_income) ** 2 for x in income_history) / len(income_history)
    std_dev = variance**0.5
    coefficient_of_variation = (std_dev / avg_income) * 100

    if coefficient_of_variation < 10:
        stability_score = 0.9
        status = "excellent"
    elif coefficient_of_variation < 20:
        stability_score = 0.75
        status = "good"
    elif coefficient_of_variation < 35:
        stability_score = 0.5
        status = "moderate"
    else:
        stability_score = 0.2
        status = "poor"

    return {
        "applicant_id": applicant_id,
        "stability_score": stability_score,
        "status": status,
        "coefficient_of_variation": round(coefficient_of_variation, 2),
        "avg_income": round(avg_income, 2),
        "current_income": income_history[-1],
    }


@server.tool()
def assess_employment_risk(applicant_id: str) -> dict:
    """Assess employment-related risk factors."""
    if applicant_id not in APPLICANT_DATA:
        return {"error": f"Applicant {applicant_id} not found"}

    profile = APPLICANT_DATA[applicant_id]

    risk_factors = {
        "Full-Time": 0.1,
        "Part-Time": 0.4,
        "Self-Employed": 0.5,
        "Freelance": 0.6,
        "Contract": 0.45,
    }

    employment_risk = risk_factors.get(profile["employment_type"], 0.5)

    if profile["employment_years"] >= 5:
        employment_risk *= 0.7
    elif profile["employment_years"] >= 2:
        employment_risk *= 0.85

    return {
        "applicant_id": applicant_id,
        "employment_type": profile["employment_type"],
        "employment_years": profile["employment_years"],
        "employment_risk_score": round(employment_risk, 2),
        "risk_level": (
            "low" if employment_risk < 0.2 else "medium" if employment_risk < 0.4 else "high"
        ),
    }


if __name__ == "__main__":
    server.run()
