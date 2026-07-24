#!/usr/bin/env python
"""System test script for Loan Approval System."""

import sys
import time
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from orchestration.state import ApplicationData, WorkflowState
from orchestration.workflow import orchestration_graph
from agents.applicant_profile_agent import analyze_applicant_profile
from agents.financial_risk_agent import analyze_financial_risk
from agents.loan_decision_agent import make_loan_decision
from agents.compliance_agent import execute_compliance_actions


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def test_applicant_profile_agent():
    """Test Applicant Profile Agent."""
    print_header("Testing Applicant Profile Agent")

    app_data = ApplicationData(
        applicant_id="APP001",
        applicant_name="John Smith",
        age=35,
        annual_income=85000,
        employment_type="Full-Time",
        employment_years=5,
        existing_liabilities=15000,
        credit_score=720,
        loan_amount=50000,
        loan_tenure_months=60,
        location="New York",
        email="john@example.com",
    )

    print("Input:")
    print(f"  Applicant: {app_data.applicant_name}")
    print(f"  Income: ${app_data.annual_income:,.2f}")
    print(f"  Employment: {app_data.employment_type} ({app_data.employment_years} years)")

    try:
        result = analyze_applicant_profile(app_data)
        print("\nProfile Analysis Results:")
        print(f"  ✅ Stability Score: {result.stability_score:.2f}")
        print(f"  ✅ Employment Risk: {result.employment_risk:.2f}")
        print(f"  ✅ Risk Level: {result.employment_risk_level}")
        print(f"  ✅ Notes: {result.analysis_notes}")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_financial_risk_agent():
    """Test Financial Risk Agent."""
    print_header("Testing Financial Risk Agent")

    app_data = ApplicationData(
        applicant_id="APP001",
        applicant_name="John Smith",
        age=35,
        annual_income=85000,
        employment_type="Full-Time",
        employment_years=5,
        existing_liabilities=15000,
        credit_score=720,
        loan_amount=50000,
        loan_tenure_months=60,
        location="New York",
        email="john@example.com",
    )

    print("Input:")
    print(f"  Annual Income: ${app_data.annual_income:,.2f}")
    print(f"  Liabilities: ${app_data.existing_liabilities:,.2f}")
    print(f"  Credit Score: {app_data.credit_score}")
    print(f"  Loan Amount: ${app_data.loan_amount:,.2f}")

    try:
        result = analyze_financial_risk(app_data)
        print("\nFinancial Risk Analysis Results:")
        print(f"  ✅ DTI Ratio: {result.dti_ratio:.2%}")
        print(f"  ✅ DTI Risk: {result.dti_risk:.2f}")
        print(f"  ✅ Credit Risk: {result.credit_risk:.2f}")
        print(f"  ✅ Loan Amount Valid: {result.loan_amount_valid}")
        print(f"  ✅ Anomalies: {len(result.anomalies)} detected")
        if result.anomalies:
            for anomaly in result.anomalies:
                print(f"     - {anomaly}")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_loan_decision_agent():
    """Test Loan Decision Agent."""
    print_header("Testing Loan Decision Agent")

    app_data = ApplicationData(
        applicant_id="APP001",
        applicant_name="John Smith",
        age=35,
        annual_income=85000,
        employment_type="Full-Time",
        employment_years=5,
        existing_liabilities=15000,
        credit_score=720,
        loan_amount=50000,
        loan_tenure_months=60,
        location="New York",
        email="john@example.com",
    )

    from orchestration.state import ProfileAnalysis, RiskAnalysis

    profile = ProfileAnalysis(
        stability_score=0.8,
        employment_risk=0.15,
        income_stability=0.8,
        employment_risk_level="low",
    )

    risk = RiskAnalysis(
        dti_ratio=0.21,
        dti_risk=0.2,
        credit_risk=0.3,
        loan_amount_valid=True,
        anomalies=[],
        anomalies_count=0,
    )

    print("Input:")
    print(f"  Applicant: {app_data.applicant_name}")
    print(f"  Profile Risk: {profile.employment_risk:.2f}")
    print(f"  Financial Risk: {risk.dti_risk:.2f}")

    try:
        result = make_loan_decision(app_data, profile, risk)
        print("\nLoan Decision Results:")
        print(f"  ✅ Decision: {result.decision}")
        print(f"  ✅ Risk Score: {result.risk_score:.3f}")
        print(f"  ✅ Confidence: {result.confidence:.0%}")
        print(f"  ✅ Rationale: {result.rationale}")
        print(f"  ✅ Key Factors:")
        for factor in result.key_factors:
            print(f"     - {factor}")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_compliance_agent():
    """Test Compliance Agent."""
    print_header("Testing Compliance Agent")

    app_data = ApplicationData(
        applicant_id="APP001",
        applicant_name="John Smith",
        age=35,
        annual_income=85000,
        employment_type="Full-Time",
        employment_years=5,
        existing_liabilities=15000,
        credit_score=720,
        loan_amount=50000,
        loan_tenure_months=60,
        location="New York",
        email="john@example.com",
    )

    from orchestration.state import LoanDecision

    decision = LoanDecision(
        decision="Approve",
        risk_score=0.32,
        confidence=0.75,
        rationale="Acceptable risk with reasonable financial metrics.",
        key_factors=["Good credit", "Stable income"],
    )

    print("Input:")
    print(f"  Application ID: APP-TEST-001")
    print(f"  Decision: {decision.decision}")
    print(f"  Applicant Email: {app_data.email}")

    try:
        result = execute_compliance_actions("APP-TEST-001", app_data, decision)
        print("\nCompliance Action Results:")
        print(f"  ✅ Case ID: {result.case_id}")
        print(f"  ✅ Action: {result.action_taken}")
        print(f"  ✅ Notification Sent: {result.notification_sent}")
        print(f"  ✅ Audit Logged: {result.audit_logged}")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_full_workflow():
    """Test complete workflow."""
    print_header("Testing Full Workflow")

    app_data = ApplicationData(
        applicant_id="APP001",
        applicant_name="John Smith",
        age=35,
        annual_income=85000,
        employment_type="Full-Time",
        employment_years=5,
        existing_liabilities=15000,
        credit_score=720,
        loan_amount=50000,
        loan_tenure_months=60,
        location="New York",
        email="john@example.com",
    )

    print("Input Application Data:")
    print(f"  Applicant: {app_data.applicant_name} (Age: {app_data.age})")
    print(f"  Income: ${app_data.annual_income:,.2f}")
    print(f"  Credit Score: {app_data.credit_score}")
    print(f"  Loan Amount: ${app_data.loan_amount:,.2f}")

    try:
        state = WorkflowState(
            application_id="APP-TEST-001",
            application_data=app_data,
        )

        print("\nExecuting workflow...")
        final_state = orchestration_graph.invoke(state)

        print("\n✅ Workflow Completed Successfully!")
        print(f"\nFinal Decision:")
        print(f"  Decision: {final_state.loan_decision.decision}")
        print(f"  Risk Score: {final_state.loan_decision.risk_score:.3f}")
        print(f"  Confidence: {final_state.loan_decision.confidence:.0%}")
        print(f"  Rationale: {final_state.loan_decision.rationale}")

        print(f"\nCase ID: {final_state.compliance_action.case_id}")
        print(f"Audit Logged: {final_state.compliance_action.audit_logged}")

        if final_state.errors:
            print(f"\n⚠️ Processing Errors: {len(final_state.errors)}")
            for error in final_state.errors:
                print(f"  - {error}")

        print(f"\nProcessing Log:")
        for log in final_state.processing_log:
            print(f"  - {log}")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("*" * 60)
    print("*  Loan Approval System - Component Tests")
    print("*" * 60)

    results = {}

    results["Profile Agent"] = test_applicant_profile_agent()
    time.sleep(1)

    results["Financial Risk Agent"] = test_financial_risk_agent()
    time.sleep(1)

    results["Loan Decision Agent"] = test_loan_decision_agent()
    time.sleep(1)

    results["Compliance Agent"] = test_compliance_agent()
    time.sleep(1)

    results["Full Workflow"] = test_full_workflow()

    print_header("Test Summary")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! System is ready to run.")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
