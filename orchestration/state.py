"""State schema for LangGraph workflow."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class ApplicationData:
    """Application input data."""
    applicant_id: str
    applicant_name: str
    age: int
    annual_income: float
    employment_type: str
    employment_years: int
    existing_liabilities: float
    credit_score: int
    loan_amount: float
    loan_tenure_months: int
    location: str
    email: str


@dataclass
class ProfileAnalysis:
    """Results from Applicant Profile Agent."""
    stability_score: float = 0.0
    employment_risk: float = 0.0
    income_stability: float = 0.0
    employment_risk_level: str = ""
    analysis_notes: str = ""


@dataclass
class RiskAnalysis:
    """Results from Financial Risk Agent."""
    dti_ratio: float = 0.0
    dti_risk: float = 0.0
    credit_risk: float = 0.0
    loan_amount_valid: bool = True
    anomalies: list = field(default_factory=list)
    anomalies_count: int = 0
    analysis_notes: str = ""


@dataclass
class LoanDecision:
    """Final loan decision."""
    decision: str = ""
    risk_score: float = 0.0
    confidence: float = 0.0
    rationale: str = ""
    key_factors: list = field(default_factory=list)
    reasoning_details: str = ""


@dataclass
class ComplianceAction:
    """Compliance and notification actions."""
    case_id: str = ""
    action_taken: str = ""
    notification_sent: bool = False
    audit_logged: bool = False


@dataclass
class WorkflowState:
    """Complete workflow state."""
    application_id: str
    application_data: ApplicationData
    profile_analysis: ProfileAnalysis = field(default_factory=ProfileAnalysis)
    risk_analysis: RiskAnalysis = field(default_factory=RiskAnalysis)
    loan_decision: LoanDecision = field(default_factory=LoanDecision)
    compliance_action: ComplianceAction = field(default_factory=ComplianceAction)
    errors: list = field(default_factory=list)
    processing_log: list = field(default_factory=list)
