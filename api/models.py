"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class DecisionType(str, Enum):
    APPROVE = "Approve"
    REJECT = "Reject"
    MANUAL_REVIEW = "Manual Review"


class LoanApplication(BaseModel):
    applicant_id: str
    applicant_name: str
    age: int = Field(..., ge=18, le=100)
    annual_income: float = Field(..., gt=0)
    employment_type: str
    employment_years: int = Field(..., ge=0)
    existing_liabilities: float = Field(..., ge=0)
    credit_score: int = Field(..., ge=300, le=850)
    loan_amount: float = Field(..., gt=0)
    loan_tenure_months: int = Field(..., gt=0)
    location: str
    email: str


class RiskAnalysis(BaseModel):
    employment_risk: float = Field(..., ge=0, le=1)
    income_stability: float = Field(..., ge=0, le=1)
    credit_risk: float = Field(..., ge=0, le=1)
    dti_risk: float = Field(..., ge=0, le=1)
    loan_amount_valid: bool
    anomalies_count: int


class Decision(BaseModel):
    decision: DecisionType
    risk_score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    rationale: str
    key_factors: List[str]
    case_id: Optional[str] = None


class ApplicationStatus(BaseModel):
    application_id: str
    applicant_id: str
    status: str
    submitted_at: str
    processed_at: Optional[str] = None
    decision: Optional[Decision] = None


class ApplicationResponse(BaseModel):
    application_id: str
    status: str
    message: str


class DecisionResponse(BaseModel):
    application_id: str
    decision: Decision
    audit_trail: Optional[dict] = None
